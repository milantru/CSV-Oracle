
using CSVOracle.Data.Enums;
using CSVOracle.Data.Interfaces;
using CSVOracle.Data.Models;
using CSVOracle.Server.Controllers;
using System.Collections.Concurrent;
using System.Text.Json;

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
		private const string additionalInfoFileName = "additional_info.txt";
		private const string additionalInfoIndexFileName = "additional_info_index.json";
		private const string reportsIndexFileName = "reports_index.json";
		private const string initialDatasetKnowledgeFileName = "initial_dataset_knowledge.json";
		private readonly ILogger<DatasetProcessorService> logger;
		private readonly IServiceScopeFactory scopeFactory;
		private readonly PythonExecutorService pythonExecutor;
		private readonly string dataFolderPath;
		private readonly Dictionary<string, string> apiKeys;

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
			this.apiKeys = config.GetSection("AppSettings:ApiKeys").Get<Dictionary<string, string>>() ?? new();
			this.scopeFactory = scopeFactory;
			this.pythonExecutor = pythonExecutor;
		}

		/// <summary>
		/// Returns the name of the ChromaDB collection used to store CSV files index for a given user and dataset.
		/// </summary>
		/// <param name="userId">The ID of the user who owns the dataset.</param>
		/// <param name="datasetId">The ID of the dataset.</param>
		/// <returns>Name of the collection for CSV files index.</returns>
		public static string GetChromaDbCollectionNameForCsvFiles(int userId, int datasetId) => $"{userId}-{datasetId}-csvFiles";

		/// <summary>
		/// Returns the name of the ChromaDB collection used to store data profiling reports index for a given user and dataset.
		/// </summary>
		/// <param name="userId">The ID of the user who owns the dataset.</param>
		/// <param name="datasetId">The ID of the dataset.</param>
		/// <returns>Name of the collection for data profiling reports index.</returns>
		public static string GetChromaDbCollectionNameForReports(int userId, int datasetId) => $"{userId}-{datasetId}-reports";

		/// <summary>
		/// Returns the name of the ChromaDB collection used to store the CSVW schema index for a given user and dataset.
		/// </summary>
		/// <param name="userId">The ID of the user who owns the dataset.</param>
		/// <param name="datasetId">The ID of the dataset.</param>
		/// <returns>Name of the collection for CSVW schema index.</returns>
		public static string GetChromaDbCollectionNameForSchema(int userId, int datasetId) => $"{userId}-{datasetId}-schema";

		/// <summary>
		/// Adds a dataset ID to the processing queue.
		/// </summary>
		/// <param name="datasetId">The ID of the dataset to enqueue for processing.</param>
		public static void EnqueueDatasetId(int datasetId)
		{
			DatasetIdsQueue.Enqueue(datasetId);
		}

		/// <summary>
		/// The main background execution loop of the service, processing datasets from the queue.
		/// </summary>
		/// <param name="stoppingToken">A cancellation token to stop the service gracefully.</param>
		/// <returns>A task representing the background execution.</returns>
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
					try
					{
						await ProcessDatasetAsync(datasetId);
						this.logger.LogInformation($"Finished processing dataset with id `{datasetId}`.");
					}
					catch (Exception e)
					{
						this.logger.LogError(e, $"Failed processing dataset with id `{datasetId}`.");

						var dataset = await TryGetDatasetAsync(datasetId);
						if (dataset is not null) // User might delete dataset
						{
							await UpdateDatasetAsync(dataset, DatasetStatus.Failed);
						}
					}
				}
			}
		}

		private async Task<Dataset?> TryGetDatasetAsync(int datasetId)
		{
			using var scope = scopeFactory.CreateScope();
			var datasetRepository = scope.ServiceProvider.GetRequiredService<IDatasetRepository>();

			var dataset = await datasetRepository.TryGetAsync(datasetId);

			return dataset;
		}

		private async Task UpdateDatasetAsync(Dataset dataset, DatasetStatus newStatus, string? initialDatasetKnowledgeJson = null)
		{
			using var scope = scopeFactory.CreateScope();
			var datasetRepository = scope.ServiceProvider.GetRequiredService<IDatasetRepository>();

			dataset.Status = newStatus;
			if (initialDatasetKnowledgeJson is not null)
			{
				dataset.InitialDatasetKnowledgeJson = initialDatasetKnowledgeJson;
			}
			await datasetRepository.UpdateAsync(dataset);
		}

		private async Task ProcessDatasetAsync(int datasetId)
		{
			// Update dataset status to processing
			var dataset = await TryGetDatasetAsync(datasetId);
			if (dataset is null) // User deleted dataset
			{
				return;
			}
			await UpdateDatasetAsync(dataset, DatasetStatus.Processing);

			// Prepare paths
			var datasetFolderPath = Path.Join(dataFolderPath, datasetId.ToString());

			var csvFilesFolderPath = Path.Join(datasetFolderPath, DatasetController.CsvFilesFolderName);
			var csvFilesPaths = Directory.GetFiles(csvFilesFolderPath, "*.csv");

			// schema is optional, if it is not provided, we won't have path to it
			string? schemaJsonFilePath = dataset.IsSchemaProvided
				? Path.Join(datasetFolderPath, DatasetController.SchemaJsonFileName)
				: null;

			var datasetMetadataJsonFilePath = Path.Join(datasetFolderPath, DatasetController.DatasetMetadataJsonFileName);

			var outputFolderPath = Path.Join(datasetFolderPath, outputFolderName);
			Directory.CreateDirectory(outputFolderPath);
			var reportsFolderPath = Path.Join(outputFolderPath, reportsFolderName);
			Directory.CreateDirectory(reportsFolderPath);
			var promptingPhasePromptsFilePath = Path.Join(outputFolderPath, promptingPhasePromptsFileName);
			var promptingPhaseInstructionsFilePath = Path.Join(outputFolderPath, promptingPhaseInstructionsFileName);
			var initialDatasetKnowledgeFilePath = Path.Join(outputFolderPath, initialDatasetKnowledgeFileName);

			// Tasks...
			var tasks = new List<Task>();

			var csvFilesCollectionName = GetChromaDbCollectionNameForCsvFiles(dataset.User.Id, dataset.Id);
			var reportsCollectionName = GetChromaDbCollectionNameForReports(dataset.User.Id, dataset.Id);
			var schemaCollectionName = dataset.IsSchemaProvided
				? GetChromaDbCollectionNameForSchema(dataset.User.Id, dataset.Id)
				: null;

			tasks.Add(Task.Run(async () =>
			{
				var generateCsvFilesIndexTask = GenerateIndex(csvFilesFolderPath, csvFilesCollectionName);

				Task? generateSchemaIndexTask = null;
				if (dataset.IsSchemaProvided)
				{
					generateSchemaIndexTask = GenerateIndex(schemaJsonFilePath!, schemaCollectionName!);
				}

				var generateDataProfilingReportsTasks = GenerateDataProfilingReports(
					csvFilesPaths, datasetMetadataJsonFilePath, reportsFolderPath);
				await Task.WhenAll(generateDataProfilingReportsTasks);

				await Task.WhenAll(
					GeneratePromptingPhasePrompts(reportsFolderPath, promptingPhasePromptsFilePath),
					GenerateIndex(reportsFolderPath, reportsCollectionName),
					generateCsvFilesIndexTask,
					generateSchemaIndexTask ?? Task.CompletedTask
				);
			}));

			tasks.Add(GeneratePromptingPhaseInstructions(csvFilesFolderPath, promptingPhaseInstructionsFilePath));

			await Task.WhenAll(tasks);
			tasks.Clear();

			List<string> collectionNames = [csvFilesCollectionName, reportsCollectionName];
			if (dataset.IsSchemaProvided)
			{
				collectionNames.Add(schemaCollectionName!);
			}
			await GenerateInitialDatasetKnowledge(collectionNames, promptingPhasePromptsFilePath,
					promptingPhaseInstructionsFilePath, initialDatasetKnowledgeFilePath);

			// Read output and update dataset
			var initialDatasetKnowledgeJson = File.ReadAllText(initialDatasetKnowledgeFilePath);

			await UpdateDatasetAsync(dataset, DatasetStatus.Processed, initialDatasetKnowledgeJson);

			// Delete dataset folder with everything in it
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

		private Task GenerateIndex(string fileOrFolderPath, string collectionName)
		{
			var args = $"-i \"{fileOrFolderPath}\" -c \"{collectionName}\"";

			var task = pythonExecutor.ExecutePythonScriptAsync("generate_index.py", args);

			return task;
		}

		private Task GenerateInitialDatasetKnowledge(List<string> collectionNames, string promptingPhasePromptsPath,
			string promptingPhaseInstructionsPath, string outputFilePath)
		{
			var options = new JsonSerializerOptions { WriteIndented = false };
			// Replace must be used to correctly escape the quotes, otherwise json.loads in Python will fail
			string collectionNamesJson = JsonSerializer.Serialize(collectionNames, options).Replace("\"", "\\\"");
			string apiKeysJson = JsonSerializer.Serialize(this.apiKeys, options);

			var args = $"-c \"{collectionNamesJson}\" -p \"{promptingPhasePromptsPath}\" " +
				$"-r \"{promptingPhaseInstructionsPath}\" -o \"{outputFilePath}\" -k \"{apiKeysJson}\"";

			var task = pythonExecutor.ExecutePythonScriptAsync("generate_initial_dataset_knowledge.py", args);

			return task;
		}
	}
}
