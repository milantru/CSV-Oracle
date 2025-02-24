using CSVOracle.Data.Enums;
using CSVOracle.Data.Interfaces;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Models
{
	public class Dataset : IEntity
	{
		public int Id { get; set; }

		public DatasetStatus Status { get; set; }

		public char? Separator { get; set; }

		public string? Encoding { get; set; }

		public string? AdditionalInfo { get; set; }

		public string? AdditionalInfoIndexJson { get; set; }
		
		public string? CsvFilesIndexJson { get; set; }

		public string? DataProfilingReportsIndexJson { get; set; }

		public List<DatasetFile> DatasetFiles { get; set; } = new();

		public string? InitialDatasetKnowledgeJson { get; set; }

		public string? ChatLlmInstructions { get; set; }

		[Required]
		public User User { get; set; } = null!;

		public List<Chat> Chats { get; set; } = new();
	}
}
