using CSVOracle.Data.Enums;
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
		/// <summary>
		/// Attempts to retrieve a dataset by its ID.
		/// </summary>
		/// <param name="datasetId">The unique identifier of the dataset.</param>
		/// <returns>
		/// A task that represents the asynchronous operation. 
		/// The task result contains the dataset if found; otherwise, <c>null</c>.
		/// </returns>
		public Task<Dataset?> TryGetAsync(int datasetId);

		/// <summary>
		/// Retrieves all datasets associated with a specific user.
		/// </summary>
		/// <param name="userId">The unique identifier of the user.</param>
		/// <returns>
		/// A task that represents the asynchronous operation. 
		/// The task result contains a list of datasets associated with the specified user.
		/// </returns>
		public Task<List<Dataset>> GetDatasetsByUserIdAsync(int userId);
	}
}
