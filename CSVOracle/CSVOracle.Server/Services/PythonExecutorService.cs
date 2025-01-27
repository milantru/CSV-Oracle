using System.Diagnostics;

namespace CSVOracle.Server.Services
{
	public class PythonExecutorService
	{
		private readonly ILogger<PythonExecutorService> logger;
		private readonly string pythonRuntimePath;
		private readonly string pythonScriptsFolderPath;

		public PythonExecutorService(ILogger<PythonExecutorService> logger, IConfiguration config)
		{
			this.logger = logger;
			this.pythonRuntimePath = config.GetRequiredSection("AppSettings:PythonRuntimePath").Value!;
			this.pythonScriptsFolderPath = config.GetRequiredSection("AppSettings:PythonScriptsFolderPath").Value!;
		}

		/// <summary>
		/// Executes a Python script (from scripts folder) asynchronously.
		/// </summary>
		/// <param name="scriptFileName">Name of the python script (with extension).</param>
		/// <param name="arguments">Cmd arguments used when executing the script.</param>
		/// <returns></returns>
		public async Task ExecutePythonScriptAsync(string scriptFileName, string arguments = "")
		{
			var scriptPath = Path.Combine(this.pythonScriptsFolderPath, scriptFileName);

			await _ExecutePythonScriptAsync(scriptPath, arguments);
		}

		private async Task _ExecutePythonScriptAsync(string scriptPath, string arguments = "")
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
