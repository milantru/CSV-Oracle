using CSVOracle.Data.Models;
using System.ComponentModel.DataAnnotations;

namespace CSVOracle.Server.Dtos
{
	public class DatasetFileDto
	{
		public int Id { get; set; }
		public string Name { get; set; } = string.Empty;

		public static DatasetFileDto From(DatasetFile datasetFile)
		{
			return new DatasetFileDto
			{
				Id = datasetFile.Id,
				Name = datasetFile.Name
			};
		}
	}
}
