using CSVOracle.Data.Interfaces;
using CSVOracle.Data.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using System.ComponentModel.DataAnnotations;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;

namespace CSVOracle.Server.Controllers
{
	[ApiController]
	[Route("[controller]")]
	public class AuthController : ControllerBase
	{
		private readonly ILogger<AuthController> logger;
		private readonly IUserRepository userRepository;
		private readonly string tokenPhrase;

		public AuthController(ILogger<AuthController> logger, IUserRepository userRepository, IConfiguration config)
		{
			this.logger = logger;
			this.userRepository = userRepository;
			this.tokenPhrase = config.GetRequiredSection("AppSettings:Token").Value!;
		}

		/// <summary>
		/// Registers a new user by hashing the password, storing the user, and returning a JWT token.
		/// </summary>
		/// <param name="user">The user object containing registration details, including raw password.</param>
		/// <returns>A JWT token if registration is successful; otherwise, a BadRequest result.</returns>
		[HttpPost("register")]
		public async Task<IActionResult> RegisterAsync(User user)
		{
			var storedUser = await userRepository.GetUserByEmailAsync(user.Email);
			var userExists = storedUser is not null;
			if (userExists)
			{
				logger.LogInformation($"Registration canceled. User with email '{user.Email}' already exists.");
				return BadRequest("This email is already in use by another user. Please choose a different email.");
			}

			/* Attention! Here is a rare case where user.Password does not contain hash, but the raw password.
			 * It is required to hash the password. */
			var passwordHash = BCrypt.Net.BCrypt.HashPassword(user.Password);
			user.Id = 0; // Defensive programming (it is expected that the id of newly creating user is 0).
			user.Password = passwordHash;

			string token = CreateToken(user, tokenPhrase);

			await userRepository.AddAsync(user);

			logger.LogInformation($"User with email '{user.Email}' has been registered successfully.");
			return Ok(token);
		}

		/// <summary>
		/// Authenticates a user by verifying the provided credentials and returns a JWT token if valid.
		/// </summary>
		/// <param name="loginCredentials">The user's login credentials.</param>
		/// <returns>A JWT token if login is successful; otherwise, a BadRequest result.</returns>
		[HttpPost("login")]
		public async Task<IActionResult> LoginAsync(LoginCredentials loginCredentials)
		{
			var storedUser = await userRepository.GetUserByEmailAsync(loginCredentials.Email);
			var userExists = storedUser is not null;
			var isPasswordCorrect = false;
			if (userExists)
			{
				/* `existingUser.Password` causes "Dereference of a possibly null reference" warning 
				 * even though `userExists` ensures it is not null, that's why `!` is used here */
				isPasswordCorrect = BCrypt.Net.BCrypt.Verify(loginCredentials.Password, storedUser!.Password);
			}

			if (!userExists || !isPasswordCorrect)
			{
				logger.LogInformation($"Login failed for email '{loginCredentials.Email}'.");
				return BadRequest("The combination of the email and the password is incorrect.");
			}

			/* The `!` operator is used here to silence "Possible null reference..." warning.
			 * `existingUser` will not be null here for sure. If it were, the `BadRequest` would have been 
			 * returned earlier in the method. */
			string token = CreateToken(storedUser!, tokenPhrase);

			logger.LogInformation($"User with email '{loginCredentials.Email}' has been logged in successfully.");
			return Ok(token);
		}

		/// <summary>
		/// Generates a JWT token for the specified user using the given secret phrase.
		/// </summary>
		/// <param name="user">The user for whom the token is to be generated.</param>
		/// <param name="tokenPhrase">The secret key used to sign the token.</param>
		/// <returns>A signed JWT token string.</returns>
		public static string CreateToken(User user, string tokenPhrase)
		{
			var claims = new List<Claim>
			{
				new Claim(ClaimTypes.Email, user.Email)
			};

			var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(tokenPhrase));
			var credentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha512Signature);

			var token = new JwtSecurityToken(
				claims: claims,
				expires: DateTime.Now.AddDays(1),
				signingCredentials: credentials
			);

			var jwt = new JwtSecurityTokenHandler().WriteToken(token);

			return jwt;
		}

		public record LoginCredentials
		{
			public required string Email { get; set; }
			public required string Password { get; set; }
		}
	}
}
