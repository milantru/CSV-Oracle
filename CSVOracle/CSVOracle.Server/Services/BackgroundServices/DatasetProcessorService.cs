
using CSVOracle.Data.Enums;
using CSVOracle.Data.Interfaces;
using CSVOracle.Server.Controllers;
using System.Collections.Concurrent;

namespace CSVOracle.Server.Services.BackgroundServices
{
	public class DatasetProcessorService : BackgroundService
	{
		private static readonly TimeSpan interval = TimeSpan.FromSeconds(30);

		private const string outputFolderName = "output";
		private const string reportsFolderName = "reports";
		private const string indicesFolderName = "indices";
		private const string promptingPhasePromptsFileName = "prompting_phase_prompts.json";
		private const string promptingPhaseInstructionsFileName = "prompting_phase_instructions.txt";
		private const string notesLlmInstructionsFileName = "notes_llm_instructions.txt";
		private const string additionalInfoFileName = "additional_info.txt";
		private const string additionalInfoIndexFileName = "additional_info_index.json";
		private const string csvFilesIndexFileName = "csv_files_index.json";
		private const string reportsIndexFileName = "reports_index.json";
		private const string initialDatasetKnowledgeFileName = "initial_dataset_knowledge.json";
		private readonly ILogger<DatasetProcessorService> logger;
		private readonly IServiceScopeFactory scopeFactory;
		private readonly PythonExecutorService pythonExecutor;
		private readonly string dataFolderPath;

		private static ConcurrentQueue<int> DatasetIdsQueue { get; } = new();

		public DatasetProcessorService(
			ILogger<DatasetProcessorService> logger,
			IConfiguration config,
			IServiceScopeFactory scopeFactory,
			PythonExecutorService pythonExecutor
		)
		{
			this.logger = logger;
			this.dataFolderPath = config.GetRequiredSection("AppSettings:DataFolderPath").Value!;
			this.scopeFactory = scopeFactory;
			this.pythonExecutor = pythonExecutor;
		}

		public static void EnqueueDatasetId(int datasetId)
		{
			DatasetIdsQueue.Enqueue(datasetId);
		}

		protected override async Task ExecuteAsync(CancellationToken stoppingToken)
		{
			while (!stoppingToken.IsCancellationRequested)
			{
				if (DatasetIdsQueue.Count == 0)
				{
					this.logger.LogInformation($"{nameof(DatasetProcessorService)} is waiting...");
					await Task.Delay(interval, stoppingToken);
					continue;
				}

				if (DatasetIdsQueue.TryDequeue(out int datasetId))
				{
					this.logger.LogInformation($"Starting processing dataset with id `{datasetId}`.");
					await ProcessDatasetAsync(datasetId);
				}
			}
		}

		private async Task ProcessDatasetAsync(int datasetId)
		{
			// Update dataset status to processing
			using var scope = scopeFactory.CreateScope();
			var datasetRepository = scope.ServiceProvider.GetRequiredService<IDatasetRepository>();

			var dataset = await datasetRepository.GetAsync(datasetId);
			dataset.Status = DatasetStatus.Processing;
			await datasetRepository.UpdateAsync(dataset);

			// Prepare paths
			var datasetFolderPath = Path.Join(dataFolderPath, datasetId.ToString());

			var csvFilesFolderPath = Path.Join(datasetFolderPath, DatasetController.CsvFilesFolderName);
			var csvFilesPaths = Directory.GetFiles(csvFilesFolderPath, "*.csv");

			var datasetMetadataJsonFilePath = Path.Join(datasetFolderPath, DatasetController.DatasetMetadataJsonFileName);

			var outputFolderPath = Path.Join(datasetFolderPath, outputFolderName);
			Directory.CreateDirectory(outputFolderPath);
			var reportsFolderPath = Path.Join(outputFolderPath, reportsFolderName);
			Directory.CreateDirectory(reportsFolderPath);
			var indicesFolderPath = Path.Join(outputFolderPath, indicesFolderName);
			Directory.CreateDirectory(indicesFolderPath);
			var promptingPhasePromptsFilePath = Path.Join(outputFolderPath, promptingPhasePromptsFileName);
			var promptingPhaseInstructionsFilePath = Path.Join(outputFolderPath, promptingPhaseInstructionsFileName);
			var notesLlmInstructionsFilePath = Path.Join(outputFolderPath, notesLlmInstructionsFileName);
			var initialDatasetKnowledgeFilePath = Path.Join(outputFolderPath, initialDatasetKnowledgeFileName);
			
			var csvFilesIndexFilePath = Path.Join(indicesFolderPath, csvFilesIndexFileName);
			var additionalInfoIndexFilePath = Path.Join(indicesFolderPath, additionalInfoIndexFileName);
			var reportsIndexFilePath = Path.Join(indicesFolderPath, reportsIndexFileName);

			// Tasks...
			var tasks = new List<Task>();

			tasks.Add(Task.Run(async () =>
			{
				var generateCsvFilesIndexTask = GenerateIndexFile(csvFilesFolderPath, csvFilesIndexFilePath);

				Task? generateAdditionalInfoIndexTask = null;
				if (!string.IsNullOrEmpty(dataset.AdditionalInfo))
				{
					var additionalInfoFilePath = Path.Join(outputFolderPath, additionalInfoFileName);
					System.IO.File.WriteAllText(additionalInfoFilePath, dataset.AdditionalInfo);

					generateAdditionalInfoIndexTask = GenerateIndexFile(additionalInfoFilePath, additionalInfoIndexFilePath);
				}

				var generateDataProfilingReportsTasks = GenerateDataProfilingReports(
					csvFilesPaths, datasetMetadataJsonFilePath, reportsFolderPath);
				await Task.WhenAll(generateDataProfilingReportsTasks);

				await Task.WhenAll(
					GeneratePromptingPhasePrompts(reportsFolderPath, promptingPhasePromptsFilePath),
					GenerateIndexFile(reportsFolderPath, reportsIndexFilePath),
					generateCsvFilesIndexTask,
					generateAdditionalInfoIndexTask ?? Task.CompletedTask
				);
			}));

			tasks.Add(GeneratePromptingPhaseInstructions(csvFilesFolderPath, promptingPhaseInstructionsFilePath));

			tasks.Add(GenerateNotesLlmInstructions(csvFilesFolderPath, notesLlmInstructionsFilePath));

			await Task.WhenAll(tasks);

			await GenerateInitialDatasetKnowledge(indicesFolderPath, promptingPhasePromptsFilePath,
					promptingPhaseInstructionsFilePath, notesLlmInstructionsFilePath, initialDatasetKnowledgeFilePath);

			// TODO Read outputs and update dataset
			tasks.Clear();

			if (dataset.AdditionalInfo is not null)
			{
				tasks.Add(Task.Run(async () =>
				{
					dataset.AdditionalInfoIndexJson = await File.ReadAllTextAsync(additionalInfoIndexFilePath);
				}));
			}
			tasks.Add(Task.Run(async () =>
			{
				dataset.CsvFilesIndexJson = await File.ReadAllTextAsync(csvFilesIndexFilePath);
			}));
			tasks.Add(Task.Run(async () =>
			{
				dataset.DataProfilingReportsIndexJson = await File.ReadAllTextAsync(reportsIndexFilePath);
			}));
			tasks.Add(Task.Run(async () =>
			{
				dataset.InitialDatasetKnowledgeJson = await File.ReadAllTextAsync(initialDatasetKnowledgeFilePath);
			}));
			tasks.Add(Task.Run(async () =>
			{
				dataset.NotesLlmInstructions = await File.ReadAllTextAsync(notesLlmInstructionsFilePath);
			}));
			//tasks.Add(Task.Run(async () =>
			//{
			//	dataset.ChatLlmInstructions = await File.ReadAllTextAsync(chatinstr);
			//}));

			await Task.WhenAll(tasks);

			dataset.Status = DatasetStatus.Processed;
			await datasetRepository.UpdateAsync(dataset);

			// TODO delete dataset folder with everything in it
			Directory.Delete(datasetFolderPath, recursive: true);
		}

		private Task GenerateDataProfilingReport(string csvFilePath, string datasetMetadataJsonFilePath, string outputFolderPath)
		{
			var args = $"-i \"{csvFilePath}\" -m \"{datasetMetadataJsonFilePath}\" -o \"{outputFolderPath}\"";

			var task = pythonExecutor.ExecutePythonScriptAsync("generate_data_profiling_report.py", args);

			return task;
		}

		private List<Task> GenerateDataProfilingReports(
			string[] csvFilesPaths, 
			string datasetMetadataJsonFilePath,
			string outputFolderPath
		)
		{
			var tasks = new List<Task>(csvFilesPaths.Length);

			foreach (var csvFilePath in csvFilesPaths)
			{
				var task = GenerateDataProfilingReport(csvFilePath, datasetMetadataJsonFilePath, outputFolderPath);
				tasks.Add(task);
			}

			return tasks;
		}

		private Task GeneratePromptingPhasePrompts(string reportsFolderPath, string outputFilePath)
		{
			var args = $"-i \"{reportsFolderPath}\" -o \"{outputFilePath}\"";

			var task = pythonExecutor.ExecutePythonScriptAsync("generate_prompting_phase_prompts.py", args);

			return task;
		}

		private Task GeneratePromptingPhaseInstructions(string csvFilesFolderPath, string outputFilePath)
		{
			var args = $"-i \"{csvFilesFolderPath}\" -o \"{outputFilePath}\"";

			var task = pythonExecutor.ExecutePythonScriptAsync("generate_prompting_phase_instructions.py", args);

			return task;
		}

		private Task GenerateNotesLlmInstructions(string csvFilesFolderPath, string outputFilePath)
		{
			var args = $"-i \"{csvFilesFolderPath}\" -o \"{outputFilePath}\"";

			var task = pythonExecutor.ExecutePythonScriptAsync("generate_notes_llm_instructions.py", args);

			return task;
		}

		private Task GenerateIndexFile(string fileOrFolderPath, string outputFilePath)
		{
			var args = $"-i \"{fileOrFolderPath}\" -o \"{outputFilePath}\"";

			var task = pythonExecutor.ExecutePythonScriptAsync("generate_index_file.py", args);

			return task;
		}

		private Task GenerateInitialDatasetKnowledge(string indicesFolderPath, string promptingPhasePromptsPath,
			string promptingPhaseInstructionsPath, string notesLlmInstructionsPath, string outputFilePath)
		{
			var args = $"-i \"{indicesFolderPath}\" -p \"{promptingPhasePromptsPath}\" -r \"{promptingPhaseInstructionsPath}\" " +
				$"-n \"{notesLlmInstructionsPath}\" -o \"{outputFilePath}\"";

			var task = pythonExecutor.ExecutePythonScriptAsync("generate_initial_dataset_knowledge.py", args);

			return task;
		}
	}
}
