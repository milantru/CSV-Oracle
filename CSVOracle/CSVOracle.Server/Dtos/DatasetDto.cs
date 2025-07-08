using CSVOracle.Data.Enums;
using CSVOracle.Data.Models;
using System.ComponentModel.DataAnnotations;

namespace CSVOracle.Server.Dtos
{
	public class DatasetDto
	{
		public int Id { get; set; }
		public DatasetStatus Status { get; set; }
		public char? Separator { get; set; }
		public string? Encoding { get; set; }
		public bool IsSchemaProvided { get; set; }
		public List<DatasetFileDto> DatasetFiles { get; set; } = new();

		/// <summary>
		/// Creates a <see cref="DatasetDto"/> instance from a given <see cref="Dataset"/> entity.
		/// </summary>
		/// <param name="dataset">The dataset entity to map from.</param>
		/// <returns>A new <see cref="DatasetDto"/> instance.</returns>
		public static DatasetDto From(Dataset dataset)
		{
			return new DatasetDto
			{
				Id = dataset.Id,
				Status = dataset.Status,
				Separator = dataset.Separator,
				Encoding = dataset.Encoding,
				IsSchemaProvided = dataset.IsSchemaProvided,
				DatasetFiles = dataset.DatasetFiles.Select(DatasetFileDto.From).ToList()
			};
		}
	}
}
