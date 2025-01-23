using CSVOracle.Data.Models;
using System.ComponentModel.DataAnnotations;

namespace CSVOracle.Server.Dtos
{
	public class ChatDto
	{
		public int Id { get; set; }
		public string Name { get; set; } = string.Empty;
		public string? UserView { get; set; } = string.Empty;
		public string MessagesJson { get; set; } = string.Empty;
		public string CurrentDatasetKnowledgeJson { get; set; } = string.Empty;

		public static ChatDto From(Chat chat)
		{
			return new ChatDto
			{
				Id = chat.Id,
				Name = chat.Name,
				UserView = chat.UserView,
				MessagesJson = chat.MessagesJson,
				CurrentDatasetKnowledgeJson = chat.CurrentDatasetKnowledgeJson
			};
		}
	}
}
