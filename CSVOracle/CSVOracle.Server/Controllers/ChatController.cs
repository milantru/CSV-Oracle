using CSVOracle.Data.Interfaces;
using CSVOracle.Data.Models;
using CSVOracle.Server.Dtos;
using CSVOracle.Server.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
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
		private readonly TokenHelper tokenHelper;

		public ChatController(
			ILogger<ChatController> logger,
			IChatRepository chatRepository,
			IDatasetRepository datasetRepository,
			TokenHelper tokenHelper
		)
		{
			this.logger = logger;
			this.chatRepository = chatRepository;
			this.datasetRepository = datasetRepository;
			this.tokenHelper = tokenHelper;
		}

		[HttpGet, Authorize]
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
		public async Task<IActionResult> AddChatAsync([FromHeader] string authorization, AddChatRequest request)
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

			var chat = new Chat
			{
				Name = request.Name,
				UserView = request.UserView,
				MessagesJson = request.MessagesJson,
				CurrentDatasetKnowledgeJson = request.CurrentDatasetKnowledgeJson,
				Dataset = dataset
			};
			await this.chatRepository.AddAsync(chat);

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
			chat.MessagesJson = chatDto.MessagesJson;
			chat.CurrentDatasetKnowledgeJson = chatDto.CurrentDatasetKnowledgeJson;
		}

		public class AddChatRequest : ChatDto // ChatDto is inherited so the class has the same properties
		{
			public int DatasetId { get; set; }
		}

		public record GenerateAnswerRequest
		{
			public string NewMessage { get; set; } = string.Empty;
			public int ChatId { get; set; }
		}
	}
}
