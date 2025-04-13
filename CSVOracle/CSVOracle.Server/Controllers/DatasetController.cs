using CSVOracle.Data.Enums;
using CSVOracle.Data.Interfaces;
using CSVOracle.Data.Models;
using CSVOracle.Server.Dtos;
using CSVOracle.Server.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Net;
using System.Text.Json;
using System.Text;
using System.Text.Json.Serialization;
using CSVOracle.Server.Services.BackgroundServices;
using Newtonsoft.Json;
using System.Net.Http.Headers;

namespace CSVOracle.Server.Controllers
{
	[ApiController]
	[Route("[controller]")]
	public class DatasetController : ControllerBase
	{
		private readonly ILogger<DatasetController> logger;
		private readonly string dataFolderPath;
		private readonly IDatasetRepository datasetRepository;
		private readonly TokenHelperService tokenHelper;
		private readonly string llmServerUrlForDeletingCollections;

		public static string CsvFilesFolderName => "csv_files";
		public static string SchemaJsonFileName => "schema.json";
		public static string DatasetMetadataJsonFileName => "metadata.json";

		public DatasetController(
			ILogger<DatasetController> logger,
			IConfiguration config,
			IDatasetRepository datasetRepository,
			TokenHelperService tokenHelper
		)
		{
			this.logger = logger;
			this.dataFolderPath = config.GetRequiredSection("AppSettings:DataFolderPath").Value!;
			this.llmServerUrlForDeletingCollections = config.GetRequiredSection("AppSettings:LlmServerUrlForDeletingCollections").Value!;
			this.datasetRepository = datasetRepository;
			this.tokenHelper = tokenHelper;
		}

		[HttpGet, Authorize]
		public async Task<IActionResult> GetUserDatasetsAsync([FromHeader] string authorization)
		{
			var user = await this.tokenHelper.GetUserAsync(authorization);
			if (user is null)
			{
				var message = "Cannot retrieve datasets for a non-existing user.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status401Unauthorized, message);
			}

			var userDatasets = await this.datasetRepository.GetDatasetsByUserIdAsync(user.Id);

			this.logger.LogInformation("Returning user datasets.");
			return Ok(userDatasets.Select(DatasetDto.From));
		}

		[HttpGet("status/{datasetId:int}"), Authorize]
		public async Task<IActionResult> GetDatasetStatusAsync([FromHeader] string authorization, int datasetId)
		{
			var user = await this.tokenHelper.GetUserAsync(authorization);
			if (user is null)
			{
				var message = "Cannot retrieve the dataset status for a non-existing user.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status401Unauthorized, message);
			}

			var userDatasets = await this.datasetRepository.GetDatasetsByUserIdAsync(user.Id);

			var status = userDatasets.FirstOrDefault(dataset => dataset.Id == datasetId)?.Status;
			if (status is null)
			{
				var message = "Cannot retrieve the dataset status, the dataset does not exist.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status404NotFound, message);
			}

			this.logger.LogInformation("Returning dataset status.");
			return Ok(status);
		}

		[HttpPost, Authorize]
		public async Task<IActionResult> EnqueueDatasetForProcessingAsync(
			[FromHeader] string authorization,
			[FromForm] List<IFormFile> csvFiles,
			IFormFile? schemaFile,
			[FromForm] DatasetMetadata metadata
		)
		{
			var user = await this.tokenHelper.GetUserAsync(authorization);
			if (user is null)
			{
				var message = "Cannot enqueue the dataset for processing for a non-existing user.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status401Unauthorized, message);
			}

			if (!ValidateCsvFiles(csvFiles))
			{
				var message = "Cannot enqueue the dataset for processing: invalid CSV file(s).";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status400BadRequest, message);
			}
			if (schemaFile is not null && !ValidateSchemaFile(schemaFile))
			{
				var message = "Cannot enqueue the dataset for processing: schema file is invalid.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status400BadRequest, message);
			}
			if (!ValidateDatasetMetadata(metadata))
			{
				var message = "Cannot enqueue the dataset for processing: dataset metadata is invalid " +
					"(maybe it contains only whitespace?).";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status400BadRequest, message);
			}

			// Create dataset and store it in the database
			var dataset = new Dataset
			{
				Status = DatasetStatus.Created,
				Separator = metadata.Separator,
				Encoding = metadata.Encoding,
				IsSchemaProvided = schemaFile is not null,
				User = user,
				DatasetFiles = csvFiles.Select(file => new DatasetFile
				{
					Name = file.FileName,
				}).ToList()
			};
			dataset = await this.datasetRepository.AddAsync(dataset);

			// Create working directory for the dataset processing
			var folderPath = Path.Join(this.dataFolderPath, dataset.Id.ToString());
			Directory.CreateDirectory(folderPath);

			// Store files and metadata in the working directory
			StoreFilesAndMetadataToFilesystem(folderPath, csvFiles, schemaFile, metadata);

			// Update dataset status and enqueue the dataset for processing
			dataset.Status = DatasetStatus.Queued;
			await this.datasetRepository.UpdateAsync(dataset);

			DatasetProcessorService.EnqueueDatasetId(dataset.Id);

			this.logger.LogInformation("Dataset has been enqueued for processing successfully.");
			return Ok(dataset.Id);
		}

		[HttpPut, Authorize]
		public async Task<IActionResult> UpdateDatasetAsync([FromHeader] string authorization, DatasetDto dataset)
		{
			var user = await this.tokenHelper.GetUserAsync(authorization);
			if (user is null)
			{
				var message = "Cannot update the dataset for a non-existing user.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status401Unauthorized, message);
			}

			Dataset storedDataset;
			try
			{
				storedDataset = await this.datasetRepository.GetAsync(dataset.Id);
			}
			catch
			{
				var message = "Cannot update the dataset, the dataset does not exist.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status404NotFound, message);
			}

			if (storedDataset.User.Id != user.Id)
			{
				var message = "Cannot update the dataset, the user requesting update is not the owner of the dataset.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status403Forbidden, message);
			}
			if (storedDataset.Status != DatasetStatus.Processed)
			{
				var message = "Cannot update the dataset, the dataset is not processed yet " +
					"(unprocessed dataset cannot be modified).";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status400BadRequest, message);
			}

			UpdateDatasetWithDtoData(storedDataset, dataset);
			await this.datasetRepository.UpdateAsync(storedDataset);

			this.logger.LogInformation("Dataset has been updated successfully.");
			return Ok();
		}

		[HttpDelete("{datasetId:int}"), Authorize]
		public async Task<IActionResult> DeleteDatasetAsync([FromHeader] string authorization, int datasetId)
		{
			var user = await this.tokenHelper.GetUserAsync(authorization);
			if (user is null)
			{
				var message = "Cannot delete the dataset for a non-existing user.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status401Unauthorized, message);
			}

			Dataset storedDataset;
			try
			{
				storedDataset = await this.datasetRepository.GetAsync(datasetId);
			}
			catch
			{
				var message = "Cannot delete the dataset, the dataset does not exist.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status404NotFound, message);
			}

			if (storedDataset.User.Id != user.Id)
			{
				var message = "Cannot delete the dataset, the user requesting deletion is not the owner of the dataset.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status403Forbidden, message);
			}

			/* Each dataset has indices and each index is stored in its Chroma DB collection.
			 * If we are deleting dataset, we won't need the indices anymore,
			 * so we delete the indices (collections) as well. */
			await DeleteIndicesAsync(storedDataset);
			await this.datasetRepository.RemoveAsync(storedDataset);

			this.logger.LogInformation("Dataset has been deleted successfully.");
			return Ok();
		}

		private async Task DeleteCollectionsAsync(List<string> collectionNames)
		{
			var args = new { collection_names = collectionNames };
			var argsJson = JsonConvert.SerializeObject(args);
			var content = new StringContent(argsJson, new MediaTypeHeaderValue("application/json"));

			using var client = new HttpClient();
			_ = await client.PostAsync(this.llmServerUrlForDeletingCollections, content);
		}

		private async Task DeleteIndicesAsync(Dataset dataset)
		{
			int userId = dataset.User.Id;
			int datasetId = dataset.Id;
			var collectionNames = new List<string>();

			var csvFilesCollectionName = DatasetProcessorService.GetChromaDbCollectionNameForCsvFiles(userId, datasetId);
			collectionNames.Add(csvFilesCollectionName);

			var reportsCollectionName = DatasetProcessorService.GetChromaDbCollectionNameForReports(userId, datasetId);
			collectionNames.Add(reportsCollectionName);

			if (dataset.IsSchemaProvided)
			{
				var schemaCollectionName = DatasetProcessorService.GetChromaDbCollectionNameForSchema(userId, datasetId);
				collectionNames.Add(schemaCollectionName);
			}

			await DeleteCollectionsAsync(collectionNames);
		}

		private static void UpdateDatasetWithDtoData(Dataset dataset, DatasetDto datasetDto)
		{
			dataset.Separator = datasetDto.Separator;
			dataset.Encoding = datasetDto.Encoding;
		}

		private static bool ValidateCsvFile(IFormFile file)
		{
			return file.Length > 0 && file.FileName.EndsWith(".csv") && file.ContentType == "text/csv";
		}

		private static bool ValidateCsvFiles(List<IFormFile> files)
		{
			return files.Count > 0 && files.All(ValidateCsvFile);
		}

		private static bool ValidateSchemaFile(IFormFile? file)
		{
			if (file is null)
			{
				return true;
			}

			return file.Length > 0 && file.FileName.EndsWith(".json") && file.ContentType == "application/json";
		}

		private static bool ValidateDatasetMetadata(DatasetMetadata metadata)
		{
			if (metadata.Encoding is not null && string.IsNullOrWhiteSpace(metadata.Encoding))
			{
				return false;
			}

			return true;
		}

		private static void StoreFilesAndMetadataToFilesystem(
			string folderPath,
			List<IFormFile> csvFiles,
			IFormFile? schemaFile,
			DatasetMetadata metadata
		)
		{
			// Create the datasets directory if it doesn't exist
			var csvFilesFolderPath = Path.Join(folderPath, CsvFilesFolderName);
			if (!Directory.Exists(csvFilesFolderPath))
			{
				Directory.CreateDirectory(csvFilesFolderPath);
			}

			// Save each CSV file to the datasets folder
			foreach (var csvFile in csvFiles)
			{
				var csvFilePath = Path.Join(csvFilesFolderPath, csvFile.FileName);

				using var fs = new FileStream(csvFilePath, FileMode.Create);
				csvFile.CopyTo(fs);
			}

			// Save schema file (if provided) to schema.json
			if (schemaFile is not null)
			{
				var schemaJsonFilePath = Path.Join(folderPath, SchemaJsonFileName);

				using var fs = new FileStream(schemaJsonFilePath, FileMode.Create);
				schemaFile.CopyTo(fs);
			}

			// Save the metadata to metadata.txt
			NormalizeDatasetMetadata(metadata);

			var metadataJson = SerializeDatasetMetadata(metadata);

			var metadataJsonFilePath = Path.Join(folderPath, DatasetMetadataJsonFileName);
			System.IO.File.WriteAllText(metadataJsonFilePath, metadataJson);
		}

		/// <summary>
		/// Normalizing is done in a way that instead of empty string we use null 
		/// and remove leading/trailing whitespace (both in additional info and encoding).
		/// </summary>
		/// <param name="metadata">Dataset metadata for normalizing</param>
		private static void NormalizeDatasetMetadata(DatasetMetadata metadata)
		{
			if (metadata.Encoding?.Length == 0)
			{
				metadata.Encoding = null;
			}
			if (metadata.Encoding is not null)
			{
				metadata.Encoding = metadata.Encoding.Trim();
			}
		}

		private static string SerializeDatasetMetadata(DatasetMetadata metadata)
		{
			return System.Text.Json.JsonSerializer.Serialize(metadata, new JsonSerializerOptions
			{
				PropertyNamingPolicy = JsonNamingPolicy.CamelCase
			});
		}

		public record DatasetMetadata
		{
			public char? Separator { get; set; }
			public string? Encoding { get; set; }
		}
	}
}
