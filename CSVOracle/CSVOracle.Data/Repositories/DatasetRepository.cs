﻿using CSVOracle.Data.Interfaces;
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

		public override async Task UpdateAsync(Dataset dataset)
		{
			var storedDataset = await CsvOracleDbContext.Datasets.FirstAsync(d => d.Id == dataset.Id);

			storedDataset.State = dataset.State;
			storedDataset.Separator = dataset.Separator;
			storedDataset.Encoding = dataset.Encoding;
			storedDataset.AdditionalInfoIndexJson = dataset.AdditionalInfoIndexJson;
			storedDataset.InitialDatasetKnowledgeJson = dataset.InitialDatasetKnowledgeJson;
			storedDataset.FirstChatMessage = dataset.FirstChatMessage;
			storedDataset.NotesLlmInstructions = dataset.NotesLlmInstructions;
			storedDataset.ChatLlmInstructions = dataset.ChatLlmInstructions;

			// User is not updated because once the dataset is assigned to the user, it is final.

			/* We update dataset files just simply by assigning (and not the way how we update chats)
			 * because by the app design we will upload only new files and we upload them just once, 
			 * all at the same time, and then the files will not be updated ever. */
			storedDataset.DatasetFiles = dataset.DatasetFiles;

			// Attention! The contents of the chats are NOT updated.
			UpdateDatasetChats(storedDataset, dataset);

			await CsvOracleDbContext.SaveChangesAsync();
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