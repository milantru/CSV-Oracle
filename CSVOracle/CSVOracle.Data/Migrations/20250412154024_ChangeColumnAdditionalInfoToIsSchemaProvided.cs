using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace CSVOracle.Data.Migrations
{
    /// <inheritdoc />
    public partial class ChangeColumnAdditionalInfoToIsSchemaProvided : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "AdditionalInfo",
                table: "Datasets");

            migrationBuilder.AddColumn<bool>(
                name: "IsSchemaProvided",
                table: "Datasets",
                type: "bit",
                nullable: false,
                defaultValue: false);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "IsSchemaProvided",
                table: "Datasets");

            migrationBuilder.AddColumn<string>(
                name: "AdditionalInfo",
                table: "Datasets",
                type: "nvarchar(max)",
                nullable: true);
        }
    }
}
