using CSVOracle.Data.Interfaces;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Models
{
	public class User : IEntity
	{
		public int Id { get; set; }
		public string Email { get; set; } = string.Empty;
		public string Password { get; set; } = string.Empty;
		public List<Dataset> Datasets { get; set; } = new();
	}
}
