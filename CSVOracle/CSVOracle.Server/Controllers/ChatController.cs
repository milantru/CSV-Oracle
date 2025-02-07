using CSVOracle.Data.Interfaces;
using CSVOracle.Data.Models;
using CSVOracle.Server.Dtos;
using CSVOracle.Server.Services;
using CSVOracle.Server.Services.BackgroundServices;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.ComponentModel.DataAnnotations;
using System.Data;
using static CSVOracle.Server.Controllers.DatasetController;

namespace CSVOracle.Server.Controllers
{
	[ApiController]
	[Route("[controller]")]
	public class ChatController : ControllerBase
	{
		private readonly ILogger<ChatController> logger;
		private readonly IChatRepository chatRepository;
		private readonly IDatasetRepository datasetRepository;
		private readonly TokenHelperService tokenHelper;
		private readonly PythonExecutorService pythonExecutor;
		private readonly string dataFolderPath;

		public ChatController(
			ILogger<ChatController> logger,
			IConfiguration config,
			IChatRepository chatRepository,
			IDatasetRepository datasetRepository,
			TokenHelperService tokenHelper,
			PythonExecutorService pythonExecutor
		)
		{
			this.logger = logger;
			this.dataFolderPath = config.GetRequiredSection("AppSettings:DataFolderPath").Value!;
			this.chatRepository = chatRepository;
			this.datasetRepository = datasetRepository;
			this.tokenHelper = tokenHelper;
			this.pythonExecutor = pythonExecutor;
		}

		[HttpGet("{datasetId:int}"), Authorize]
		public async Task<IActionResult> GetDatasetChatsAsync([FromHeader] string authorization, int datasetId)
		{
			var user = await this.tokenHelper.GetUserAsync(authorization);
			if (user is null)
			{
				var message = "Cannot retrieve the dataset chats for a non-existing user.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status401Unauthorized, message);
			}

			Dataset dataset;
			try
			{
				dataset = await this.datasetRepository.GetAsync(datasetId);
			}
			catch
			{
				var message = "Cannot retrieve the dataset chats, the dataset does not exist.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status404NotFound, message);
			}

			if (dataset.User.Id != user.Id)
			{
				var message = "Cannot retrieve the dataset chats, the dataset does not belong to the user.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status403Forbidden, message);
			}

			this.logger.LogInformation("Returning dataset chats.");
			return Ok(dataset.Chats.Select(ChatDto.From));
		}

		[HttpPost, Authorize]
		public async Task<IActionResult> AddChatAsync([FromHeader] string authorization, [FromForm] AddChatRequest request)
		{
			var user = await this.tokenHelper.GetUserAsync(authorization);
			if (user is null)
			{
				var message = "Cannot create the dataset chat for a non-existing user.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status401Unauthorized, message);
			}

			Dataset dataset;
			try
			{
				dataset = await this.datasetRepository.GetAsync(request.DatasetId);
			}
			catch
			{
				var message = "Cannot create the dataset chat, the dataset does not exist.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status404NotFound, message);
			}

			// TODO Refactor
			var userView = NormalizeUserView(request.UserView);

			var chatFolderPath = Path.Join(this.dataFolderPath, Guid.NewGuid().ToString());
			Directory.CreateDirectory(chatFolderPath);

			string indicesFolderPath = Path.Join(chatFolderPath, "indices");
			Directory.CreateDirectory(indicesFolderPath);
			if (dataset.AdditionalInfoIndexJson is not null)
			{
				System.IO.File.WriteAllText(
					Path.Join(indicesFolderPath, "additional_info_index.json"), dataset.AdditionalInfoIndexJson);
			}
			System.IO.File.WriteAllText(Path.Join(indicesFolderPath, "csv_files_index.json"), dataset.CsvFilesIndexJson);
			System.IO.File.WriteAllText(Path.Join(indicesFolderPath, "reports_index.json"), dataset.DataProfilingReportsIndexJson);

			string datasetKnowledgeFilePath = Path.Join(chatFolderPath, "dataset_knowledge.json");
			System.IO.File.WriteAllText(datasetKnowledgeFilePath, dataset.InitialDatasetKnowledgeJson);

			string? userViewFilePath = userView is not null ? Path.Join(chatFolderPath, "user_view.txt") : null;
			if (userViewFilePath is not null)
			{
				System.IO.File.WriteAllText(userViewFilePath, userView);
			}

			string messageFilePath = Path.Join(chatFolderPath, "message.txt");
			string startMessage = userView is null ? "Please write \"Hello! How can I help you with this dataset?\"."
				: "If you can deduce the user need based on the user view, write the answer (provide only answer, " +
				"no questions, e.g. \"Would you like assistance with some specific task?\"). If you cannot deduce the user need " +
				"based on the user view, just write \"Hello! How can I help you with this dataset?\".";
			System.IO.File.WriteAllText(messageFilePath, startMessage);

			string notesLlmInstructionsFilePath = Path.Join(chatFolderPath, "notes_llm_instructions.txt");
			System.IO.File.WriteAllText(notesLlmInstructionsFilePath, dataset.NotesLlmInstructions);

			string updatedChatHistoryFilePath = Path.Join(chatFolderPath, "updated_chat_history.json");
			string updatedDatasetKnowledgeFilePath = Path.Join(chatFolderPath, "updated_dataset_knowledge.json");
			string answerFilePath = Path.Join(chatFolderPath, "answer.txt");

			await _GenerateAnswerAsync(indicesFolderPath, datasetKnowledgeFilePath, userViewFilePath, null, 
				messageFilePath, notesLlmInstructionsFilePath, updatedChatHistoryFilePath, 
				updatedDatasetKnowledgeFilePath, answerFilePath);

			string chatHistoryJson = System.IO.File.ReadAllText(updatedChatHistoryFilePath);
			string? updatedDatasetKnowledgeJson = null;
			if (System.IO.File.Exists(updatedDatasetKnowledgeFilePath))
			{
				updatedDatasetKnowledgeJson = System.IO.File.ReadAllText(updatedDatasetKnowledgeFilePath);
			}
			string answer = System.IO.File.ReadAllText(answerFilePath);

			var chat = new Chat
			{
				Name = request.Name,
				UserView = userView,
				ChatHistoryJson = chatHistoryJson,
				CurrentDatasetKnowledgeJson = updatedDatasetKnowledgeJson ?? dataset.InitialDatasetKnowledgeJson!,
				Dataset = dataset
			};
			await this.chatRepository.AddAsync(chat);

			Directory.Delete(chatFolderPath, recursive: true);

			this.logger.LogInformation("Chat has been created successfully.");
			return Ok();
		}

		[HttpPost("generate-answer"), Authorize]
		public async Task<IActionResult> GenerateAnswerAsync([FromHeader] string authorization, GenerateAnswerRequest request)
		{
			await Task.CompletedTask;
			throw new NotImplementedException();
		}

		[HttpPut, Authorize]
		public async Task<IActionResult> UpdateChatAsync([FromHeader] string authorization, ChatDto chat)
		{
			var user = await this.tokenHelper.GetUserAsync(authorization);
			if (user is null)
			{
				var message = "Cannot update the dataset chat for a non-existing user.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status401Unauthorized, message);
			}

			Chat storedChat;
			try
			{
				storedChat = await this.chatRepository.GetAsync(chat.Id);
			}
			catch
			{
				var message = "Cannot update the dataset chat, the chat does not exist.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status404NotFound, message);
			}

			UpdateChatWithDtoData(storedChat, chat);
			await this.chatRepository.UpdateAsync(storedChat);

			this.logger.LogInformation("Chat has been updated successfully.");
			return Ok();
		}

		[HttpDelete, Authorize]
		public async Task<IActionResult> DeleteChatAsync([FromHeader] string authorization, ChatDto chat)
		{
			var user = await this.tokenHelper.GetUserAsync(authorization);
			if (user is null)
			{
				var message = "Cannot delete the dataset chat for a non-existing user.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status401Unauthorized, message);
			}

			Chat storedChat;
			try
			{
				storedChat = await this.chatRepository.GetAsync(chat.Id);
			}
			catch
			{
				var message = "Cannot delete the dataset chat, the chat does not exist.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status404NotFound, message);
			}

			bool chatBelongsToUser = user.Datasets.Select(d => d.Id).Contains(storedChat.Dataset.Id);
			if (!chatBelongsToUser)
			{
				var message = "Cannot delete the dataset chat, the chat does not belong to the user.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status403Forbidden, message);
			}

			await this.chatRepository.RemoveAsync(storedChat);

			this.logger.LogInformation("Chat has been deleted successfully.");
			return Ok();
		}

		private static void UpdateChatWithDtoData(Chat chat, ChatDto chatDto)
		{
			chat.Name = chatDto.Name;
			chat.UserView = chatDto.UserView;

			/* ChatHistoryJson and CurrentDatasetKnowledgeJson are not being updated here, 
			 * because they can be updated only when chatting. */
		}

		private static string? NormalizeUserView(string? userView)
		{
			string? userViewTrimmedOrNull = userView?.Trim();
			if (string.IsNullOrEmpty(userViewTrimmedOrNull))
			{
				return null;
			}

			// returns non empty trimmed string (not null, nor just whitespace)
			return userViewTrimmedOrNull;
		}

		private async Task _GenerateAnswerAsync(string indicesFolderPath, string datasetKnowledgeFilePath,
			string? userViewFilePath, string? chatHistoryFilePath, string messageFilePath,
			string notesLlmInstructionsFilePath, string updatedChatHistoryFilePath,
			string updatedDatasetKnowledgeFilePath, string answerFilePath)
		{
			var args = $"-i \"{indicesFolderPath}\" -d \"{datasetKnowledgeFilePath}\"";
			if (userViewFilePath is not null)
			{
				args = args + $" -u \"{userViewFilePath}\"";
			}
			if (chatHistoryFilePath is not null)
			{
				args = args + $" -c \"{chatHistoryFilePath}\"";
			}
			args = args + $" -m \"{messageFilePath}\" -n \"{notesLlmInstructionsFilePath}\" " +
				$"-s \"{updatedChatHistoryFilePath}\" -t \"{updatedDatasetKnowledgeFilePath}\" -a \"{answerFilePath}\"";

			await this.pythonExecutor.ExecutePythonScriptAsync("generate_answer.py", args);
		}

		public record AddChatRequest
		{
			[Required]
			public string Name { get; set; } = null!;
			public string? UserView { get; set; }
			public int DatasetId { get; set; }
		}

		public record GenerateAnswerRequest
		{
			public string NewMessage { get; set; } = string.Empty;
			public int ChatId { get; set; }
		}
	}
}
