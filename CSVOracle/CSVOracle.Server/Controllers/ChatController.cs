using CSVOracle.Data.Enums;
using CSVOracle.Data.Interfaces;
using CSVOracle.Data.Models;
using CSVOracle.Server.Dtos;
using CSVOracle.Server.Services;
using CSVOracle.Server.Services.BackgroundServices;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using System.ComponentModel.DataAnnotations;
using System.Data;
using System.Net.Http.Headers;
using System.Text.Json;

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
		private readonly string dataFolderPath;
		private readonly Dictionary<string, string> apiKeys;
		private readonly string llmServerUrlForGeneratingAnswer;

		public ChatController(
			ILogger<ChatController> logger,
			IConfiguration config,
			IChatRepository chatRepository,
			IDatasetRepository datasetRepository,
			TokenHelperService tokenHelper
		)
		{
			this.logger = logger;
			this.dataFolderPath = config.GetRequiredSection("AppSettings:DataFolderPath").Value!;
			this.apiKeys = config.GetRequiredSection("AppSettings:ApiKeys").Get<Dictionary<string, string>>()!;
			this.llmServerUrlForGeneratingAnswer = config.GetRequiredSection("AppSettings:LlmServerUrlForGeneratingAnswer").Value!;
			this.chatRepository = chatRepository;
			this.datasetRepository = datasetRepository;
			this.tokenHelper = tokenHelper;
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

		[HttpGet("dataset-knowledge/{chatId:int}"), Authorize]
		public async Task<IActionResult> GetDatasetKnowledgeAsync([FromHeader] string authorization, int chatId)
		{
			var user = await this.tokenHelper.GetUserAsync(authorization);
			if (user is null)
			{
				var message = "Cannot retrieve the dataset knowledge for a non-existing user.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status401Unauthorized, message);
			}

			Chat chat;
			try
			{
				chat = await this.chatRepository.GetAsync(chatId);
			}
			catch
			{
				var message = "Cannot retrieve the chat, it does not exist.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status404NotFound, message);
			}

			if (!user.Datasets.Select(d => d.Id).Contains(chat.Dataset.Id))
			{
				var message = "Cannot retrieve the dataset knowledge, it does not belong to the user.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status403Forbidden, message);
			}

			this.logger.LogInformation("Returning dataset knowledge.");
			return Ok(chat.CurrentDatasetKnowledgeJson);
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

			if (dataset.Status != DatasetStatus.Processed)
			{
				var message = "Cannot create the dataset chat, the dataset is not processed yet.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status400BadRequest, message);
			}

			var userView = NormalizeUserView(request.UserView);

			string? chatHistoryJson = null;
			string? chatFolderPath = null;
			string? updatedDatasetKnowledgeJson = null;
			bool answeringUserViewFailed = false;
			if (userView is not null)
			{
				try
				{
					// We try to answer user need based on user view directly, but this may fail, e.g. due to reaching max iterations.
					chatFolderPath = Path.Join(this.dataFolderPath, Guid.NewGuid().ToString());
					Directory.CreateDirectory(chatFolderPath);

					var startMessage = "If you can deduce the user need based on the user view, write the answer (provide only answer, " +
						"no questions, e.g. \"Would you like assistance with some specific task?\"). If you cannot deduce the user need " +
						"based on the user view, then without using any tool just write \"Hello! How can I help you with this dataset?\".";
					var collectionNames = GetCollectionNames(dataset.User.Id, dataset);

					(chatHistoryJson, updatedDatasetKnowledgeJson) = await _GenerateAnswerAsync(
						chatFolderPath, collectionNames, dataset.InitialDatasetKnowledgeJson!, userView, null, startMessage);

					var chatMessages = ChatDto.ChatHistory.FromChatHistoryJson(chatHistoryJson);
					/* Last message should contain either the answer to the user need coming from user view or default sentence,
					* e.g. "Hello! How can I help you with this dataset?". We want to display only this message at the beginning
					* of the chat. */
					var lastChatMessage = chatMessages.Last();
					chatHistoryJson = ChatDto.ChatHistory.ToChatHistoryJson(new List<ChatDto.ChatMessage> { lastChatMessage });
				}
				catch (Exception e)
				{
					this.logger.LogWarning(e, "Asistant failed to deduce and answer user need from user view, probably reached max iterations.");
					answeringUserViewFailed = true; // This way we can fallback to the case as if we didn't have the user view.
				}
			}

			if (userView is null || answeringUserViewFailed)
			{
				var startMessage = "Hello! How can I help you with this dataset?";
				var chatMessage = new ChatDto.ChatMessage(
					role: ChatDto.ChatMessageRole.Assistant,
					text: startMessage
				);
				var chatHistory = new List<ChatDto.ChatMessage> { chatMessage };
				chatHistoryJson = ChatDto.ChatHistory.ToChatHistoryJson(chatHistory);
			}

			var chat = new Chat
			{
				Name = request.Name,
				UserView = userView,
				ChatHistoryJson = chatHistoryJson!,
				CurrentDatasetKnowledgeJson = updatedDatasetKnowledgeJson ?? dataset.InitialDatasetKnowledgeJson!,
				Dataset = dataset
			};
			await this.chatRepository.AddAsync(chat);

			if (Directory.Exists(chatFolderPath))
			{
				/* We tried to answer user need based on the user view directly,
				 * so the folder was created, we can delete it now. */
				Directory.Delete(chatFolderPath, recursive: true);
			}

			this.logger.LogInformation("Chat has been created successfully.");
			return Ok();
		}

		[HttpPost("generate-answer"), Authorize]
		public async Task<IActionResult> GenerateAnswerAsync([FromHeader] string authorization,
			[FromForm] GenerateAnswerRequest request)
		{
			var user = await this.tokenHelper.GetUserAsync(authorization);
			if (user is null)
			{
				var message = "Cannot generate answer for a non-existing user.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status401Unauthorized, message);
			}

			Chat chat;
			try
			{
				chat = await this.chatRepository.GetAsync(request.ChatId);
			}
			catch
			{
				var message = "Cannot generate answer, the chat does not exist.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status404NotFound, message);
			}

			var chatFolderPath = Path.Join(this.dataFolderPath, Guid.NewGuid().ToString());
			Directory.CreateDirectory(chatFolderPath);

			var collectionNames = GetCollectionNames(user.Id, chat.Dataset);

			string updatedChatHistoryFilePath = null!;
			string? updatedDatasetKnowledgeFilePath = null;
			try
			{
				(updatedChatHistoryFilePath, updatedDatasetKnowledgeFilePath) = await _GenerateAnswerAsync(
					chatFolderPath, collectionNames, chat.CurrentDatasetKnowledgeJson, chat.UserView, chat.ChatHistoryJson, request.NewMessage);
			}
			catch (Exception e)
			{
				/* This should not happen, if it happened, most likely the LLM tried many times to use some tool or something, couldn't,
				 * reached max iteractions and thus did not generated answer. Although it is unlikely to happen, theoretically it can happen.
				 * When the user tries again to generate answer, it most likely will generate answer without a problem.
				 * The reason why WE are not trying to regenerate answer again is that if this happened, the user probably waited long enough, 
				 * so we want to display something, change UI. And also, what IF there appeared some other problem and not the one described.
				 * We certainly want to discover such a problem and solve it, so if the problem persists, let the user report it so it can be solved. */
				var message = "Failed to generate answer. Please try again. If the problem persists, contact the admin.";
				this.logger.LogWarning(e, message);
				Directory.Delete(chatFolderPath, recursive: true); // Clean temporary chat folder
				return StatusCode(StatusCodes.Status500InternalServerError, message);
			}

			chat.ChatHistoryJson = updatedChatHistoryFilePath;
			if (updatedDatasetKnowledgeFilePath is not null)
			{
				chat.CurrentDatasetKnowledgeJson = updatedDatasetKnowledgeFilePath;
			}
			await this.chatRepository.UpdateAsync(chat);

			Directory.Delete(chatFolderPath, recursive: true);

			this.logger.LogInformation("Answer has been generated successfully.");
			return Ok(ChatDto.From(chat));
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

		[HttpDelete("{chatId:int}"), Authorize]
		public async Task<IActionResult> DeleteChatAsync([FromHeader] string authorization, int chatId)
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
				storedChat = await this.chatRepository.GetAsync(chatId);
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

		/// <summary>
		/// Normalizes a user view string by trimming whitespace and converting empty or whitespace-only strings to null.
		/// </summary>
		/// <param name="userView">The input user view string to normalize. May be null or contain whitespace.</param>
		/// <returns>
		/// A trimmed, non-empty string if the input is not null or whitespace-only; otherwise, returns null.
		/// </returns>
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

		private List<string> GetCollectionNames(int userId, Dataset dataset)
		{
			List<string> collectionNames = [
				DatasetProcessorService.GetChromaDbCollectionNameForCsvFiles(userId, dataset.Id),
					DatasetProcessorService.GetChromaDbCollectionNameForReports(userId, dataset.Id)
			];
			if (dataset.IsSchemaProvided)
			{
				collectionNames.Add(
					DatasetProcessorService.GetChromaDbCollectionNameForSchema(userId, dataset.Id)
				);
			}

			return collectionNames;
		}

		private async Task<(
			string DatasetKnowledgeFilePath,
			string? UserViewFilePath,
			string? ChatHistoryFilePath,
			string MessageFilePath
		)> WriteInputsAsync(string chatFolderPath, string datasetKnowledgeJson, string? userView, string? chatHistoryJson, string message)
		{
			var writingTasks = new List<Task>();

			string datasetKnowledgeFilePath = Path.Join(chatFolderPath, "dataset_knowledge.json");
			writingTasks.Add(Task.Run(() => System.IO.File.WriteAllText(datasetKnowledgeFilePath, datasetKnowledgeJson)));

			var userViewFilePath = userView is not null ? Path.Join(chatFolderPath, "user_view.txt") : null;
			if (userViewFilePath is not null)
			{
				writingTasks.Add(Task.Run(() => System.IO.File.WriteAllText(userViewFilePath, userView)));
			}

			var chatHistoryFilePath = chatHistoryJson is not null ? Path.Join(chatFolderPath, "chat_history.json") : null;
			if (chatHistoryFilePath is not null)
			{
				writingTasks.Add(Task.Run(() => System.IO.File.WriteAllText(chatHistoryFilePath, chatHistoryJson)));
			}

			string messageFilePath = Path.Join(chatFolderPath, "message.txt");
			System.IO.File.WriteAllText(messageFilePath, message);

			await Task.WhenAll(writingTasks);
			return (datasetKnowledgeFilePath, userViewFilePath, chatHistoryFilePath, messageFilePath);
		}

		private async Task<(string ChatHistoryJson, string? UpdatedDatasetKnowledgeJson)> ReadOutputsAsync(
			string updatedChatHistoryFilePath, string updatedDatasetKnowledgeFilePath)
		{
			var readingTasks = new List<Task>();
			string chatHistoryJson = null!;
			string? updatedDatasetKnowledgeJson = null;

			if (System.IO.File.Exists(updatedDatasetKnowledgeFilePath))
			{
				readingTasks.Add(Task.Run(() => chatHistoryJson = System.IO.File.ReadAllText(updatedChatHistoryFilePath)));
				readingTasks.Add(Task.Run(() => updatedDatasetKnowledgeJson = System.IO.File.ReadAllText(updatedDatasetKnowledgeFilePath)));
				await Task.WhenAll(readingTasks);
				readingTasks.Clear();
			}
			else
			{
				chatHistoryJson = System.IO.File.ReadAllText(updatedChatHistoryFilePath);
			}

			await Task.WhenAll(readingTasks);
			return (chatHistoryJson, updatedDatasetKnowledgeJson);
		}

		private async Task<(string ChatHistoryJson, string? UpdatedDatasetKnowledgeJson)> _GenerateAnswerAsync(
			string chatFolderPath, List<string> collectionNames, string datasetKnowledgeJson, string? userView, string? chatHistoryJson, string message)
		{
			// Write inputs to disk so Python script can read it
			var (datasetKnowledgeFilePath, userViewFilePath, chatHistoryFilePath, messageFilePath) = await WriteInputsAsync(
				chatFolderPath, datasetKnowledgeJson, userView, chatHistoryJson, message);

			// Prepare paths for outputs
			string updatedChatHistoryFilePath = Path.Join(chatFolderPath, "updated_chat_history.json");
			string updatedDatasetKnowledgeFilePath = Path.Join(chatFolderPath, "updated_dataset_knowledge.json");

			// Generate answer
			var options = new JsonSerializerOptions { WriteIndented = false };
			string apiKeysJson = System.Text.Json.JsonSerializer.Serialize(this.apiKeys, options);

			var args = new
			{
				collection_names = collectionNames,
				dataset_knowledge_path = datasetKnowledgeFilePath,
				user_view_path = userViewFilePath,
				chat_history_path = chatHistoryFilePath,
				message_path = messageFilePath,
				updated_chat_history_path = updatedChatHistoryFilePath,
				updated_dataset_knowledge_path = updatedDatasetKnowledgeFilePath,
				api_keys = apiKeysJson
			};
			var argsJson = JsonConvert.SerializeObject(args);
			var content = new StringContent(argsJson, new MediaTypeHeaderValue("application/json"));

			using var client = new HttpClient();
			client.Timeout = TimeSpan.FromMinutes(10); // Sometimes LLM needs more time to think, that's why timeout is increased here
			_ = await client.PostAsync(this.llmServerUrlForGeneratingAnswer, content);

			// Read outputs
			var (updatedChatHistoryJson, updatedDatasetKnowledgeJson) = await ReadOutputsAsync(
				updatedChatHistoryFilePath, updatedDatasetKnowledgeFilePath);

			return (updatedChatHistoryJson, updatedDatasetKnowledgeJson);
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
