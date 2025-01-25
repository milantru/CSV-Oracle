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

namespace CSVOracle.Server.Controllers
{
	[ApiController]
	[Route("[controller]")]
	public class DatasetController : ControllerBase
	{
		private const string datasetsFolderName = "datasets";
		private const string datasetMetadataJsonFileName = "metadata.json";
		private readonly ILogger<DatasetController> logger;
		private readonly string dataFolderPath;
		private readonly IDatasetRepository datasetRepository;
		private readonly TokenHelperService tokenHelper;

		public DatasetController(
			ILogger<DatasetController> logger,
			IConfiguration config,
			IDatasetRepository datasetRepository, 
			TokenHelperService tokenHelper
		)
		{
			this.logger = logger;
			this.dataFolderPath = config.GetRequiredSection("AppSettings:DataFolderPath").Value!;
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

		[HttpGet("status"), Authorize]
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
			[FromForm] List<IFormFile> files,
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

			if (!ValidateCsvFiles(files))
			{
				var message = "Cannot enqueue the dataset for processing, file (or files) were invalid.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status400BadRequest, message);
			}
			if (!ValidateDatasetMetadata(metadata))
			{
				var message = "Cannot enqueue the dataset for processing, dataset metadata is invalid " +
					"(maybe it contains only whitespace?).";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status400BadRequest, message);
			}

			// Create dataset and store it in the database
			var dataset = new Dataset
			{
				Status = DatasetStatus.Created,
				AdditionalInfo = metadata.AdditionalInfo,
				Separator = metadata.Separator,
				Encoding = metadata.Encoding,
				User = user
			};
			dataset = await this.datasetRepository.AddAsync(dataset);

			// Create working directory for the dataset processing
			var folderPath = Path.Join(this.dataFolderPath, dataset.Id.ToString());
			Directory.CreateDirectory(folderPath);

			// Store files and metadata in the working directory
			StoreCsvFilesAndMetadataToFilesystem(folderPath, files, metadata);

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

		[HttpDelete, Authorize]
		public async Task<IActionResult> DeleteDatasetAsync([FromHeader] string authorization, DatasetDto dataset)
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
				storedDataset = await this.datasetRepository.GetAsync(dataset.Id);
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

			await this.datasetRepository.RemoveAsync(storedDataset);

			this.logger.LogInformation("Dataset has been deleted successfully.");
			return Ok();
		}

		private static void UpdateDatasetWithDtoData(Dataset dataset, DatasetDto datasetDto)
		{
			dataset.Separator = datasetDto.Separator;
			dataset.Encoding = datasetDto.Encoding;
			dataset.AdditionalInfo = datasetDto.AdditionalInfo;
		}

		private static bool ValidateCsvFile(IFormFile file)
		{
			return file.Length > 0 && file.FileName.EndsWith(".csv") && file.ContentType == "text/csv";
		}

		private static bool ValidateCsvFiles(List<IFormFile> files)
		{
			return files.Count > 0 && files.All(ValidateCsvFile);
		}

		private static bool ValidateDatasetMetadata(DatasetMetadata metadata)
		{
			if (metadata.AdditionalInfo is not null && string.IsNullOrWhiteSpace(metadata.AdditionalInfo))
			{
				return false;
			}
			if (metadata.Encoding is not null && string.IsNullOrWhiteSpace(metadata.Encoding))
			{
				return false;
			}

			return true;
		}

		private static void StoreCsvFilesAndMetadataToFilesystem(string folderPath, List<IFormFile> files, DatasetMetadata metadata)
		{
			// Create the datasets directory if it doesn't exist
			var datasetsFolderPath = Path.Combine(folderPath, datasetsFolderName);
			if (!Directory.Exists(datasetsFolderPath))
			{
				Directory.CreateDirectory(datasetsFolderPath);
			}

			// Save each CSV file to the datasets folder
			foreach (var file in files)
			{
				var filePath = Path.Combine(datasetsFolderPath, file.FileName);

				using var fs = new FileStream(filePath, FileMode.Create);
				file.CopyTo(fs);
			}

			// Save the metadata to metadata.txt
			NormalizeDatasetMetadata(metadata);

			var metadataJson = SerializeDatasetMetadata(metadata);

			var metadataJsonFilePath = Path.Combine(folderPath, datasetMetadataJsonFileName);
			System.IO.File.WriteAllText(metadataJsonFilePath, metadataJson);
		}

		/// <summary>
		/// Normalizing is done in a way that instead of empty string we use null 
		/// and remove leading/trailing whitespace (both in additional info and encoding).
		/// </summary>
		/// <param name="metadata">Dataset metadata for normalizing</param>
		private static void NormalizeDatasetMetadata(DatasetMetadata metadata)
		{
			if (metadata.AdditionalInfo?.Length == 0)
			{
				metadata.AdditionalInfo = null;
			}
			if (metadata.AdditionalInfo is not null)
			{
				metadata.AdditionalInfo = metadata.AdditionalInfo.Trim();
			}

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
			return JsonSerializer.Serialize(metadata, new JsonSerializerOptions
			{
				PropertyNamingPolicy = JsonNamingPolicy.CamelCase
			});
		}

		public record DatasetMetadata
		{
			public char? Separator { get; set; }
			public string? Encoding { get; set; }
			public string? AdditionalInfo { get; set; }
		}
	}
}
