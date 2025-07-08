using CSVOracle.Data.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Interfaces
{
	public interface IUserRepository : IRepository<User>
	{
		/// <summary>
		/// Retrieves a user by their email address.
		/// </summary>
		/// <param name="email">The email address of the user.</param>
		/// <returns>
		/// A task that represents the asynchronous operation. 
		/// The task result contains the user if found; otherwise, <c>null</c>.
		/// </returns>
		public Task<User?> GetUserByEmailAsync(string email);
	}
}
