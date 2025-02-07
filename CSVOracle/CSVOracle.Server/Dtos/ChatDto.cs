using CSVOracle.Data.Models;
using Newtonsoft.Json;
using System.ComponentModel.DataAnnotations;

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
			var chatMessages = JsonConvert.DeserializeObject<List<ChatMessage>>(chat.ChatHistoryJson)!;
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

		public class ChatMessage
		{
			public string Role { get; set; } = null!;
			public Dictionary<string, object> AdditionalKwargs { get; set; } = null!;
			public List<Block> Blocks { get; set; } = null!;
		}

		public class Block
		{
			public string BlockType { get; set; } = null!;
			public string Text { get; set; } = null!;
		}
	}
}
