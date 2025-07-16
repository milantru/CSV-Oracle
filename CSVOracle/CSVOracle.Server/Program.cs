using CSVOracle.Data;
using CSVOracle.Data.Interfaces;
using CSVOracle.Data.Repositories;
using CSVOracle.Server.Services;
using CSVOracle.Server.Services.BackgroundServices;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using Swashbuckle.AspNetCore.Filters;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.

builder.Services.AddCors(options =>
{
	options.AddPolicy("AllowAllHeaders",
		builder =>
		{
			builder
			.AllowAnyOrigin()
			.AllowAnyHeader()
			.AllowAnyMethod();
		});
});

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
	options.AddSecurityDefinition("oauth2", new OpenApiSecurityScheme
	{
		Description = "Standard Authorization header using the Bearer scheme  (\"bearer {token}\")",
		In = ParameterLocation.Header,
		Name = "Authorization",
		Type = SecuritySchemeType.ApiKey
	});

	options.OperationFilter<SecurityRequirementsOperationFilter>();
});

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
	.AddJwtBearer(options =>
	{
		options.TokenValidationParameters = new TokenValidationParameters
		{
			ValidateIssuerSigningKey = true,
			IssuerSigningKey = new SymmetricSecurityKey(
				key: Encoding.UTF8.GetBytes(builder.Configuration.GetRequiredSection("AppSettings:Token").Value!)
			),
			ValidateIssuer = false,
			ValidateAudience = false
		};
	});

builder.Services.AddDbContext<CSVOracleDbContext>(options =>
{
	var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
	options.UseSqlServer(connectionString);
});
builder.Services.AddScoped<IDatasetRepository, DatasetRepository>();
builder.Services.AddScoped<IChatRepository, ChatRepository>();
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<TokenHelperService>();

builder.Services.AddSingleton<PythonExecutorService>();

builder.Services.AddHostedService<DatasetProcessorService>();

var app = builder.Build();

app.UseDefaultFiles();
app.UseStaticFiles();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
	app.UseSwagger();
	app.UseSwaggerUI();
}

app.UseCors("AllowAllHeaders");

app.UseAuthentication();

app.UseAuthorization();

app.MapControllers();

app.MapFallbackToFile("/index.html");

Console.WriteLine("Application server starting");
app.Run();
