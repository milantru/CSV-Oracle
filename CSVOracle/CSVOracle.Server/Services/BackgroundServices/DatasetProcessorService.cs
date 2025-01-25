
using CSVOracle.Data.Interfaces;
using System.Collections.Concurrent;

namespace CSVOracle.Server.Services.BackgroundServices
{
	public class DatasetProcessorService : BackgroundService
	{
		private readonly ILogger<DatasetProcessorService> logger;
		private readonly IServiceScopeFactory scopeFactory;
		private readonly PythonExecutorService pythonExecutor;

		private static ConcurrentQueue<int> DatasetIdsQueue { get; } = new();

		public DatasetProcessorService(
			ILogger<DatasetProcessorService> logger,
			IServiceScopeFactory scopeFactory,
			PythonExecutorService pythonExecutor
		)
		{
			this.logger = logger;
			this.scopeFactory = scopeFactory;
			this.pythonExecutor = pythonExecutor;
		}

		public static void EnqueueDatasetId(int datasetId)
		{
			DatasetIdsQueue.Enqueue(datasetId);
		}

		protected override async Task ExecuteAsync(CancellationToken stoppingToken)
		{
			while (!stoppingToken.IsCancellationRequested)
			{
				if (DatasetIdsQueue.Count == 0)
				{
					this.logger.LogInformation($"{nameof(DatasetProcessorService)} is waiting...");
					await Task.Delay(1000, stoppingToken);
					continue;
				}

				if (DatasetIdsQueue.TryDequeue(out int datasetId))
				{
					this.logger.LogInformation($"Starting processing dataset with id `{datasetId}`.");
					ProcessDatasetAsync(datasetId);
				}
			}
		}

		private void ProcessDatasetAsync(int datasetId)
		{
			throw new NotImplementedException();
		}
	}
}
