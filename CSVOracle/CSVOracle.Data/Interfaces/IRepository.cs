using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Interfaces
{
	public interface IRepository<TEntity> where TEntity : class, IEntity
	{
		/// <summary>
		/// Retrieves an entity by its unique identifier.
		/// </summary>
		/// <param name="id">The unique identifier of the entity.</param>
		/// <returns>
		/// A task that represents the asynchronous operation 
		/// with result containing the entity.
		/// </returns>
		public Task<TEntity> GetAsync(int id);

		/// <summary>
		/// Adds a new entity to the repository.
		/// </summary>
		/// <param name="entity">The entity to add.</param>
		/// <returns>
		/// A task that represents the asynchronous operation. 
		/// The task result contains the added entity (with generated ID).
		/// </returns>
		public Task<TEntity> AddAsync(TEntity entity);

		/// <summary>
		/// Updates an existing entity in the repository.
		/// </summary>
		/// <param name="entity">The entity to update.</param>
		/// <returns>A task that represents the asynchronous operation.</returns>
		public abstract Task UpdateAsync(TEntity entity);

		/// <summary>
		/// Removes an entity from the repository.
		/// </summary>
		/// <param name="entity">The entity to remove.</param>
		/// <returns>A task that represents the asynchronous operation.</returns>
		public Task RemoveAsync(TEntity entity);
	}
}
