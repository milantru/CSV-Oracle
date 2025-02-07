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
		public string Name { get; set; } = null!;

		public string? UserView { get; set; }

		[Required]
		public string ChatHistoryJson { get; set; } = null!;

		[Required]
		public string CurrentDatasetKnowledgeJson { get; set; } = null!;

		[Required]
		public Dataset Dataset { get; set; } = null!;
	}
}
