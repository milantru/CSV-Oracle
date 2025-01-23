using CSVOracle.Data.Enums;
using CSVOracle.Data.Models;
using System.ComponentModel.DataAnnotations;

namespace CSVOracle.Server.Dtos
{
	public class DatasetDto
	{
		public int Id { get; set; }
		public char? Separator { get; set; }
		public string? Encoding { get; set; }
		public string? AdditionalInfo { get; set; }

		public static DatasetDto From(Dataset dataset)
		{
			return new DatasetDto
			{
				Id = dataset.Id,
				Separator = dataset.Separator,
				Encoding = dataset.Encoding,
				AdditionalInfo = dataset.AdditionalInfo
			};
		}
	}
}
