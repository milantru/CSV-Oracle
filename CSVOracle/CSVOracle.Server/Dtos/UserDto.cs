using CSVOracle.Data.Models;
using System.ComponentModel.DataAnnotations;

namespace CSVOracle.Server.Dtos
{
	public class UserDto
	{
		public int Id { get; set; }
		public string Email { get; set; } = string.Empty;

		public static UserDto From(User user)
		{
			return new UserDto
			{
				Id = user.Id,
				Email = user.Email
			};
		}
	}
}
