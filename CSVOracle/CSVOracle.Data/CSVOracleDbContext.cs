using CSVOracle.Data.Models;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data
{
	public class CSVOracleDbContext : DbContext
	{
		public DbSet<Dataset> Datasets { get; set; }
		public DbSet<DatasetFile> DatasetFiles { get; set; }
		public DbSet<Chat> Chats { get; set; }
		public DbSet<User> Users { get; set; }

		public CSVOracleDbContext(DbContextOptions<CSVOracleDbContext> options) : base(options)
		{

		}
	}
}
