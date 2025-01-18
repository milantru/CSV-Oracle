using CSVOracle.Data.Interfaces;
using CSVOracle.Data.Models;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Repositories
{
	public class UserRepository : RepositoryBase<User>, IUserRepository
	{
		public CSVOracleDbContext CsvOracleDbContext => (CSVOracleDbContext)dbContext;
		public UserRepository(CSVOracleDbContext csvOracleDbContext) : base(csvOracleDbContext)
		{
			
		}

		public override async Task UpdateAsync(User user)
		{
			var storedUser = await CsvOracleDbContext.Users.FirstAsync(u => u.Id == user.Id);

			storedUser.Email = user.Email;
			storedUser.Password = user.Password;

			// Attention! The contents of datasets are NOT updated.
			UpdateUserDatasets(storedUser, user);

			await CsvOracleDbContext.SaveChangesAsync();
		}

		public async Task<User?> GetUserByEmailAsync(string email)
		{
			return await CsvOracleDbContext.Users.FirstOrDefaultAsync(u => u.Email == email);
		}

		private void UpdateUserDatasets(User storedUser, User user)
		{
			var existingDatasetsIds = new List<int>();
			var newDatasets = new List<Dataset>();

			foreach (var dataset in user.Datasets)
			{
				if (dataset.Id == 0)
				{
					newDatasets.Add(dataset);
				}
				else
				{
					existingDatasetsIds.Add(dataset.Id);
				}
			}
			storedUser.Datasets = CsvOracleDbContext.Datasets.Where(d => existingDatasetsIds.Contains(d.Id)).ToList();
			storedUser.Datasets.AddRange(newDatasets);
		}
	}
}
