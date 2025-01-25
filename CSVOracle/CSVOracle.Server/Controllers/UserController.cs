using CSVOracle.Data.Interfaces;
using CSVOracle.Data.Models;
using CSVOracle.Server.Dtos;
using CSVOracle.Server.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Net;
using System.Security.Claims;
using System.Text;

namespace CSVOracle.Server.Controllers
{
	[ApiController]
	[Route("[controller]")]
	public class UserController : ControllerBase
	{
		private readonly ILogger<UserController> logger;
		private readonly IConfiguration config;
		private readonly IUserRepository userRepository;
		private readonly TokenHelperService tokenHelper;

		public UserController(
			ILogger<UserController> logger, 
			IConfiguration config, 
			IUserRepository userRepository,
			TokenHelperService tokenHelper
		)
		{
			this.logger = logger;
			this.config = config;
			this.userRepository = userRepository;
			this.tokenHelper = tokenHelper;
		}

		[HttpGet, Authorize]
		public async Task<IActionResult> GetCurrentlyLoggedInUserAsync([FromHeader] string authorization)
		{
			var user = await this.tokenHelper.GetUserAsync(authorization);
			if (user is null)
			{
				var message = "Cannot return currently logged in user, it seems the user does not exist " +
					"(maybe it was deleted recently?).";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status404NotFound, message);
			}

			this.logger.LogInformation("Returning currently logged in user.");
			return Ok(UserDto.From(user));
		}

		[HttpPut, Authorize]
		public async Task<IActionResult> UpdateUserAsync(
			[FromHeader] string authorization, 
			[FromBody] UpdateUserRequest updateUserRequest
		)
		{
			var user = await this.tokenHelper.GetUserAsync(authorization);
			if (user is null)
			{
				var message = "Cannot update the user, the user does not exist.";
				this.logger.LogInformation(message);
				return StatusCode(StatusCodes.Status400BadRequest, message);
			}

			var (isValid, errorMessage) = await ValidateAsync(updateUserRequest, user!);
			if (!isValid)
			{
				this.logger.LogInformation($"Cannot update the user ({errorMessage}).");
				return StatusCode(StatusCodes.Status400BadRequest, errorMessage!);

			}

			// Update user data
			user!.Email = updateUserRequest.Email;

			if (!updateUserRequest.OldPassword.IsNullOrEmpty() && !updateUserRequest.NewPassword.IsNullOrEmpty())
			{// Password change requested
				if (!BCrypt.Net.BCrypt.Verify(updateUserRequest.OldPassword, user.Password))
				{
					var message = "The password is incorrect.";
					this.logger.LogInformation($"Cannot update user ({message}).");
					return StatusCode(StatusCodes.Status403Forbidden, message);
				}

				user.Password = BCrypt.Net.BCrypt.HashPassword(updateUserRequest.NewPassword);
			}

			/* After changing email, the new token must be generated as it contains email (email claim) 
			 * and sent back to the client so it can be stored in local storage. */
			var tokenPhrase = config.GetRequiredSection("AppSettings:Token").Value!;
			var token = AuthController.CreateToken(user, tokenPhrase);

			await userRepository.UpdateAsync(user);

			this.logger.LogInformation($"User updated successfully.");
			return Ok(token);
		}

		private async Task<(bool isValid, string? errorMessage)> ValidateAsync(UpdateUserRequest updateUserRequest, User user)
		{
			if (user!.Email != updateUserRequest.Email)
			{
				var tmpUser = await userRepository.GetUserByEmailAsync(updateUserRequest.Email);
				if (tmpUser is not null)
				{
					return (false, "Email is already used by someone else.");
				}
			}

			var isOldPasswordMissing = updateUserRequest.OldPassword.IsNullOrEmpty();
			var isNewPasswordMissing = updateUserRequest.NewPassword.IsNullOrEmpty();
			if ((isOldPasswordMissing && !isNewPasswordMissing)
				|| (!isOldPasswordMissing && isNewPasswordMissing))
			{
				return (false, "Both old password and new password must be provided together, " +
					"or neither should be provided.");
			}

			return (true, null);
		}

		// Inheritance is used here so the UpdateUserRequest has the same properties as UserDto.
		public class UpdateUserRequest : UserDto
		{
			public string? OldPassword { get; set; }
			public string? NewPassword { get; set; }
		}
	}
}
