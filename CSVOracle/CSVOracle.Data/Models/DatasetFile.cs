using CSVOracle.Data.Interfaces;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Models
{
	public class DatasetFile : IEntity
	{
		public int Id { get; set; }
		public string CsvFileIndexJson { get; set; } = string.Empty;
		public string DataProfilingIndexJson { get; set; } = string.Empty;
		public Dataset Dataset { get; set; } = new();
	}
}
