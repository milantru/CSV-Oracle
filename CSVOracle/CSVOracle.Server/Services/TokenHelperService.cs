using CSVOracle.Data.Interfaces;
using CSVOracle.Data.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;

namespace CSVOracle.Server.Services
{
	public class TokenHelperService
	{
		private const string authorizationHeaderPrefix = "bearer ";
		private readonly string tokenPhrase;
		private readonly IUserRepository userRepository;

		public TokenHelperService(IConfiguration config, IUserRepository userRepository)
		{
			this.tokenPhrase = config.GetRequiredSection("AppSettings:Token").Value!;
			this.userRepository = userRepository;
		}

		/// <summary>
		/// Extracts the user associated with the given authorization token.
		/// </summary>
		/// <param name="authorizationHeader">Authorization header containing the JWT token.</param>
		/// <returns>
		/// The corresponding <see cref="User"/> object if the token is valid and the user exists; otherwise, <c>null</c>.
		/// </returns>
		public async Task<User?> GetUserAsync(string authorizationHeader)
		{
			var email = GetUserEmail(authorizationHeader);
			if (email is null)
			{
				return null;
			}

			var user = await userRepository.GetUserByEmailAsync(email);
			if (user is null)
			{
				/* This should not happen as username is from token, but defensive programming...
				 * Probably the only way this could happen is if the user was deleted 
				 * and the token has not expired yet. */
				return null;
			}

			return user;
		}

		private string? GetEmailFromToken(string token)
		{
			var key = Encoding.UTF8.GetBytes(this.tokenPhrase);

			try
			{
				var tokenValidationParameters = new TokenValidationParameters
				{
					ValidateIssuerSigningKey = true,
					IssuerSigningKey = new SymmetricSecurityKey(key),
					ValidateIssuer = false,
					ValidateAudience = false,
					// Set clockskew to zero so tokens expire exactly at token expiration time (instead of 5 minutes later)
					ClockSkew = TimeSpan.Zero
				};

				var principal = new JwtSecurityTokenHandler()
					.ValidateToken(token, tokenValidationParameters, out SecurityToken validatedToken);

				var emailClaim = principal.FindFirst(ClaimTypes.Email);

				return emailClaim!.Value;
			}
			catch (Exception)
			{
				// Token validation failed
				return null;
			}
		}

		private string? GetUserEmail(string authorizationHeader)
		{
			string? email = null;

			if (authorizationHeader.StartsWith(authorizationHeaderPrefix))
			{
				var token = authorizationHeader.Substring(authorizationHeaderPrefix.Length);
				email = GetEmailFromToken(token);
			}

			return email;
		}
	}
}
