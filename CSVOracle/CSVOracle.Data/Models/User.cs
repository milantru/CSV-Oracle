using CSVOracle.Data.Interfaces;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Models
{
	public class User : IEntity
	{
		public int Id { get; set; }

		// MaxLength is set according to:
		// https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
		[Required, EmailAddress, MaxLength(254)]
		public string Email { get; set; } = string.Empty;

		[Required]
		public string Password { get; set; } = string.Empty;

		public List<Dataset> Datasets { get; set; } = new();
	}
}
