using CSVOracle.Data.Interfaces;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Models
{
	public class Chat : IEntity
	{
		public int Id { get; set; }

		[Required]
		public string Name { get; set; } = string.Empty;

		public string? UserView { get; set; } = string.Empty;

		[Required]
		public string FirstChatMessage { get; set; } = string.Empty;

		[Required]
		public string MessagesJson { get; set; } = string.Empty;

		[Required]
		public string CurrentDatasetKnowledgeJson { get; set; } = string.Empty;

		[Required]
		public Dataset Dataset { get; set; } = null!;
	}
}
