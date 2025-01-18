using CSVOracle.Data.Interfaces;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Models
{
	public class Chat : IEntity
	{
		public int Id { get; set; }
		public int Name { get; set; }
		public string UserView { get; set; } = string.Empty;
		public string MessagesJson { get; set; } = string.Empty;
		public string CurrentDatasetKnowledgeJson { get; set; } = string.Empty;
		public Dataset Dataset { get; set; } = new();
	}
}
