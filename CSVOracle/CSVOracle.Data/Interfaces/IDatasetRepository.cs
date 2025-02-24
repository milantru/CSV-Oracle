﻿using CSVOracle.Data.Enums;
using CSVOracle.Data.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Interfaces
{
	public interface IDatasetRepository : IRepository<Dataset>
	{
		public Task<List<Dataset>> GetDatasetsByUserIdAsync(int userId);
	}
}
