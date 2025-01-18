using CSVOracle.Data.Enums;
using CSVOracle.Data.Interfaces;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Models
{
	public class Dataset : IEntity
	{
		public int Id { get; set; }
		public DatasetState State { get; set; }
		public char? Separator { get; set; }
		public string? Encoding { get; set; }
		public string? AdditionalInfoIndexJson { get; set; }
		public List<DatasetFile> DatasetFiles { get; set; } = new();
		public string? InitialDatasetKnowledgeJson { get; set; }
		public string? FirstChatMessage { get; set; }
		public string? NotesLlmInstructions { get; set; }
		public string? ChatLlmInstructions { get; set; }
		public User User { get; set; } = new();
		public List<Chat> Chats { get; set; } = new();
	}
}
