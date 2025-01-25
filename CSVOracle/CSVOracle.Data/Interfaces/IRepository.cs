using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Interfaces
{
	public interface IRepository<TEntity> where TEntity : class, IEntity
	{
		public Task<TEntity> GetAsync(int id);
		public Task<IEnumerable<TEntity>> GetAsync(Func<TEntity, bool> predicate);
		public Task<IEnumerable<TEntity>> GetAsync();
		public Task<TEntity> AddAsync(TEntity entity);
		public abstract Task UpdateAsync(TEntity entity);
		public Task RemoveAsync(TEntity entity);
	}
}
