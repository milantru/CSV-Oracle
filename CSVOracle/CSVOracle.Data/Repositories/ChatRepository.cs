using CSVOracle.Data.Interfaces;
using CSVOracle.Data.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Repositories
{
	public class ChatRepository : RepositoryBase<Chat>, IChatRepository
	{
		public CSVOracleDbContext CsvOracleDbContext => (CSVOracleDbContext)dbContext;

		public ChatRepository(CSVOracleDbContext csvOracleDbContext) : base(csvOracleDbContext)
		{

		}

		public override async Task<Chat> AddAsync(Chat chat)
		{
			/* We attach the dataset because we don't want to create a new dataset in the database, 
			 * we want to use the existing one. */
			CsvOracleDbContext.Attach(chat.Dataset);

			CsvOracleDbContext.Add(chat);

			await CsvOracleDbContext.SaveChangesAsync();

			// After saving changes, the chat will have id set correctly.
			return CsvOracleDbContext.Chats.AsNoTracking()
				.Include(c => c.Dataset)
				.First(c => c.Id == chat.Id);
		}

		public override async Task UpdateAsync(Chat chat)
		{
			var storedChat = await CsvOracleDbContext.Chats.FirstAsync(c => c.Id == chat.Id);

			storedChat.Name = chat.Name;
			storedChat.UserView = chat.UserView;
			storedChat.ChatHistoryJson = chat.ChatHistoryJson;
			storedChat.CurrentDatasetKnowledgeJson = chat.CurrentDatasetKnowledgeJson;

			// We do not update the dataset because once the chat is assigned to the dataset, it is final.

			await CsvOracleDbContext.SaveChangesAsync();
		}

		public override async Task<Chat> GetAsync(int chatId)
		{
			await Task.CompletedTask;
			return CsvOracleDbContext.Chats.AsNoTracking()
				.Include(c => c.Dataset)
				.First(c => c.Id == chatId);
		}
	}
}
