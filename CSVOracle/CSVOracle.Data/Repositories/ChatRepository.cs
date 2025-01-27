﻿using CSVOracle.Data.Interfaces;
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

		public override async Task UpdateAsync(Chat chat)
		{
			var storedChat = await CsvOracleDbContext.Chats.FirstAsync(c => c.Id == chat.Id);

			storedChat.Name = chat.Name;
			storedChat.UserView = chat.UserView;
			storedChat.FirstChatMessage = chat.FirstChatMessage;
			storedChat.MessagesJson = chat.MessagesJson;
			storedChat.CurrentDatasetKnowledgeJson = chat.CurrentDatasetKnowledgeJson;

			// We do not update the dataset because once the chat is assigned to the dataset, it is final.

			await CsvOracleDbContext.SaveChangesAsync();
		}

		public override async Task<Chat> GetAsync(int chatId)
		{
			return await CsvOracleDbContext.Chats.AsNoTracking()
				.Include(c => c.Dataset)
				.FirstAsync(c => c.Id == chatId);
		}
	}
}
