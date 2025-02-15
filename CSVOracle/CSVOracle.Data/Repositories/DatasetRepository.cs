using CSVOracle.Data.Enums;
using CSVOracle.Data.Interfaces;
using CSVOracle.Data.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Repositories
{
	public class DatasetRepository : RepositoryBase<Dataset>, IDatasetRepository
	{
		public CSVOracleDbContext CsvOracleDbContext => (CSVOracleDbContext)dbContext;

		public DatasetRepository(CSVOracleDbContext csvOracleDbContext) : base(csvOracleDbContext)
		{
			
		}

		public override async Task<Dataset> AddAsync(Dataset dataset)
		{
			CsvOracleDbContext.AddRange(dataset.DatasetFiles);
			/* We attach the user because we don't want to create a new user in the database, 
			 * we want to use the existing one. */
			CsvOracleDbContext.Attach(dataset.User);

			CsvOracleDbContext.Add(dataset);

			await CsvOracleDbContext.SaveChangesAsync();

			/* After Add method, the entity is being tracked. We do not want to return tracked entity,
			 * so the new query is executed with AsNoTracking. After SaveChanges method call the entity 
			 * will have valid id (EF Core will take care of that). */
			return await CsvOracleDbContext.Datasets.AsNoTracking()
				.Include(d => d.User)
				.Include(d => d.DatasetFiles)
				.FirstAsync(e => e.Id == dataset.Id);
		}

		public override async Task UpdateAsync(Dataset dataset)
		{
			var storedDataset = await CsvOracleDbContext.Datasets.FirstAsync(d => d.Id == dataset.Id);

			storedDataset.Status = dataset.Status;
			storedDataset.Separator = dataset.Separator;
			storedDataset.Encoding = dataset.Encoding;
			storedDataset.AdditionalInfo = dataset.AdditionalInfo;
			storedDataset.AdditionalInfoIndexJson= dataset.AdditionalInfoIndexJson;
			storedDataset.CsvFilesIndexJson= dataset.CsvFilesIndexJson;
			storedDataset.DataProfilingReportsIndexJson = dataset.DataProfilingReportsIndexJson;
			storedDataset.InitialDatasetKnowledgeJson = dataset.InitialDatasetKnowledgeJson;
			storedDataset.NotesLlmInstructions = dataset.NotesLlmInstructions;
			storedDataset.ChatLlmInstructions = dataset.ChatLlmInstructions;

			// User is not updated because once the dataset is assigned to the user (when creating dataset), it is final.

			// DatasetFiles are not updated because we add them just once, when the dataset is created.

			// Status is not updated, it is being updated only when processing

			// Attention! The contents of the chats are NOT updated.
			UpdateDatasetChats(storedDataset, dataset);

			await CsvOracleDbContext.SaveChangesAsync();
		}

		public override async Task<Dataset> GetAsync(int datasetId)
		{
			await Task.CompletedTask;
			return CsvOracleDbContext.Datasets.AsNoTracking()
				.Include(d => d.DatasetFiles)
				.Include(d => d.User)
				.Include(d => d.Chats)
				.First(d => d.Id == datasetId);
		}

		public async Task<List<Dataset>> GetDatasetsByUserIdAsync(int userId)
		{
			await Task.CompletedTask;
			return CsvOracleDbContext.Datasets.AsNoTracking()
				.Include(d => d.DatasetFiles)
				.Include(d => d.User)
				.Include(d => d.Chats)
				.Where(d => d.User.Id == userId)
				.ToList();
		}

		private void UpdateDatasetChats(Dataset storedDataset, Dataset dataset)
		{
			var existingChatsIds = new List<int>();
			var newChats = new List<Chat>();

			foreach (var chat in dataset.Chats)
			{
				if (chat.Id == 0)
				{
					newChats.Add(chat);
				}
				else
				{
					existingChatsIds.Add(chat.Id);
				}
			}
			storedDataset.Chats = CsvOracleDbContext.Chats.Where(c => existingChatsIds.Contains(c.Id)).ToList();
			storedDataset.Chats.AddRange(newChats);
		}
	}
}
