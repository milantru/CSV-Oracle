using CSVOracle.Data.Interfaces;
using CSVOracle.Data.Models;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Repositories
{
	public abstract class RepositoryBase<TEntity> : IRepository<TEntity> where TEntity : class, IEntity
	{
		protected readonly DbContext dbContext;

		public RepositoryBase(DbContext dbContext)
		{
			/* Is it OK to store DbContext in the field and to register it as a scoped service? (AddDbContext in Program.cs 
			 * uses Scoped by default). It should be short lived, right?
			 * Well, according to the docs it's fine as long as "the default injection scope is used", 
			 * see https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/#implicitly-sharing-dbcontext-instances-via-dependency-injection */
			this.dbContext = dbContext;
		}

		public virtual async Task<TEntity> AddAsync(TEntity entity)
		{
			dbContext.Set<TEntity>().Add(entity);

			await dbContext.SaveChangesAsync();

			/* After Add method, the entity is being tracked. We do not want to return tracked entity,
			 * so the new query is executed. After SaveChanges method call the entity will have valid id
			 * (EF Core will take care of that). */
			return await dbContext.Set<TEntity>().AsNoTracking().FirstAsync(e => e.Id == entity.Id);
		}

		public virtual async Task<TEntity> GetAsync(int id)
		{
			var entity = await dbContext.Set<TEntity>().AsNoTracking().FirstAsync(e => e.Id == id);

			return entity;
		}

		public virtual async Task<IEnumerable<TEntity>> GetAsync(Func<TEntity, bool> predicate)
		{
			var entities = dbContext.Set<TEntity>().AsNoTracking().Where(predicate);

			await Task.CompletedTask;
			return entities;
		}

		public virtual async Task<IEnumerable<TEntity>> GetAsync()
		{
			var entities = await dbContext.Set<TEntity>().AsNoTracking().ToListAsync();

			return entities;
		}

		public async Task RemoveAsync(TEntity entity)
		{
			dbContext.Set<TEntity>().Remove(entity);

			await dbContext.SaveChangesAsync();
		}

		public abstract Task UpdateAsync(TEntity entity);
	}
}
