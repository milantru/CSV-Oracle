using System.Diagnostics;

namespace CSVOracle.Server.Services
{
	public class PythonExecutorService
	{
		private readonly ILogger<PythonExecutorService> logger;
		private readonly string pythonRuntimePath;

		public PythonExecutorService(ILogger<PythonExecutorService> logger, IConfiguration config)
		{
			this.logger = logger;
			this.pythonRuntimePath = config.GetRequiredSection("AppSettings:PythonRuntimePath").Value!;
		}

		public async Task ExecutePythonScriptAsync(string scriptPath, string arguments = "")
		{
			var startInfo = new ProcessStartInfo
			{
				FileName = this.pythonRuntimePath,
				Arguments = $"{scriptPath} {arguments}",
				RedirectStandardOutput = true,
				RedirectStandardError = true,
				UseShellExecute = false,
				CreateNoWindow = true,
			};

			using var process = new Process { StartInfo = startInfo };

			await Task.Run(() =>
			{
				process.Start();
				string result = process.StandardOutput.ReadToEnd();
				string error = process.StandardError.ReadToEnd();
				process.WaitForExit();

				if (!string.IsNullOrEmpty(result))
				{
					logger.LogInformation($"Python script output: {result}");
				}

				if (!string.IsNullOrEmpty(error))
				{
					logger.LogError($"Python script error: {error}");
				}
			});
		}
	}
}
