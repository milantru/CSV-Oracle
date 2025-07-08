using CSVOracle.Data.Models;
using System.ComponentModel.DataAnnotations;

namespace CSVOracle.Server.Dtos
{
	public class DatasetFileDto
	{
		public int Id { get; set; }
		public string Name { get; set; } = string.Empty;

		/// <summary>
		/// Creates a <see cref="DatasetFileDto"/> instance from a given <see cref="DatasetFile"/> entity.
		/// </summary>
		/// <param name="datasetFile">The dataset file entity to map from.</param>
		/// <returns>A new <see cref="DatasetFileDto"/> instance.</returns>
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
