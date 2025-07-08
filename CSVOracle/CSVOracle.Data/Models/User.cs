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

		/// <summary>
		/// Gets or sets the user's email address.
		/// Must be a valid email format and no longer than 254 characters,
		/// based on the commonly accepted maximum length for email addresses
		/// (<see href="https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address" />).
		/// </summary>
		[Required, EmailAddress, MaxLength(254)]
		public string Email { get; set; } = string.Empty;

		[Required]
		public string Password { get; set; } = string.Empty;

		public List<Dataset> Datasets { get; set; } = new();
	}
}
