﻿using CSVOracle.Data.Interfaces;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Models
{
	public class DatasetFile : IEntity
	{
		public int Id { get; set; }

		[Required]
		public string Name { get; set; } = string.Empty;

		[Required]
		public Dataset Dataset { get; set; } = null!;
	}
}
