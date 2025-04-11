using CSVOracle.Data.Models;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;

namespace CSVOracle.Server.Dtos
{
	public class ChatDto
	{
		public int Id { get; set; }
		public string Name { get; set; } = null!;
		public string? UserView { get; set; }
		public List<string> Messages { get; set; } = null!;
		public string CurrentDatasetKnowledgeJson { get; set; } = null!;

		public static ChatDto From(Chat chat)
		{
			var chatMessages = ChatHistory.FromChatHistoryJson(chat.ChatHistoryJson);
			List<string> messages = chatMessages.Select(m => string.Join("\n\n", m.Blocks.Select(b => b.Text))).ToList();

			return new ChatDto
			{
				Id = chat.Id,
				Name = chat.Name,
				UserView = chat.UserView,
				Messages = messages,
				CurrentDatasetKnowledgeJson = chat.CurrentDatasetKnowledgeJson
			};
		}

		public enum ChatMessageRole
		{
			User,
			Assistant
		}

		public class Block
		{
			public string BlockType { get; set; } = null!;
			public string Text { get; set; } = null!;
		}

		public class ChatMessage
		{
			public string Role { get; set; } = null!; // "user" or "assistant"
			public Dictionary<string, object> AdditionalKwargs { get; set; } = null!;
			public List<Block> Blocks { get; set; } = null!;

			[JsonConstructor]
			public ChatMessage()
			{
				// Empty
			}

			public ChatMessage(ChatMessageRole role, string text)
			{
				Role = GetRoleString(role);
				AdditionalKwargs = new Dictionary<string, object>();
				Blocks = new List<Block>
				{
					new Block{
						BlockType = "text",
						Text = text
					}
				};
			}

			private string GetRoleString(ChatMessageRole role) =>
				role switch
				{
					ChatMessageRole.User => "user",
					ChatMessageRole.Assistant => "assistant",
					_ => throw new Exception($"Unknown {nameof(ChatMessageRole)} value.")
				};
		}

		public static class ChatHistory
		{
			private static readonly JsonSerializerSettings defaultSettings = new()
			{
				ContractResolver = new DefaultContractResolver
				{
					NamingStrategy = new SnakeCaseNamingStrategy()
				}
			};

			public static string ToChatHistoryJson(List<ChatMessage> chatMessages)
			{
				var chatHistoryJson = JsonConvert.SerializeObject(chatMessages, defaultSettings);

				return chatHistoryJson;
			}

			public static List<ChatMessage> FromChatHistoryJson(string chatHistoryJson)
			{
				var chatHistory = JsonConvert.DeserializeObject<List<ChatMessage>>(chatHistoryJson, defaultSettings);
				if (chatHistory is null)
				{
					throw new Exception("Invalid chat history JSON, cannot deserialize.");
				}

				return chatHistory;
			}
		}
	}
}
