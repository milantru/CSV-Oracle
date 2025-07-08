using CSVOracle.Data.Models;
using System.ComponentModel.DataAnnotations;

namespace CSVOracle.Server.Dtos
{
	public class UserDto
	{
		public int Id { get; set; }
		public string Email { get; set; } = string.Empty;

		/// <summary>
		/// Creates a <see cref="UserDto"/> instance from a given <see cref="User"/> entity.
		/// </summary>
		/// <param name="user">The user entity to map from.</param>
		/// <returns>A new <see cref="UserDto"/> instance.</returns>
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
