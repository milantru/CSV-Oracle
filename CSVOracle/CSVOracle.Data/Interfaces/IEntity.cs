using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CSVOracle.Data.Interfaces
{
	public interface IEntity
	{
		/// <summary>
		/// Gets or sets the unique identifier of the entity.
		/// </summary>
		public int Id { get; set; }
	}
}
