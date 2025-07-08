using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Enums
{
	/// <summary>
	/// Represents the processing status of a dataset.
	/// </summary>
	public enum DatasetStatus
	{
		/// <summary>
		/// The dataset has been created but not yet queued for processing.
		/// </summary>
		Created,

		/// <summary>
		/// The dataset is queued and awaiting processing.
		/// </summary>
		Queued,

		/// <summary>
		/// The dataset is currently being processed.
		/// </summary>
		Processing,

		/// <summary>
		/// The dataset has been successfully processed.
		/// </summary>
		Processed,

		/// <summary>
		/// Processing the dataset failed.
		/// </summary>
		Failed
	}
}
