using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace CSVOracle.Data.Migrations
{
    /// <inheritdoc />
    public partial class RemoveIndicesColumns : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "AdditionalInfoIndexJson",
                table: "Datasets");

            migrationBuilder.DropColumn(
                name: "CsvFilesIndexJson",
                table: "Datasets");

            migrationBuilder.DropColumn(
                name: "DataProfilingReportsIndexJson",
                table: "Datasets");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "AdditionalInfoIndexJson",
                table: "Datasets",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "CsvFilesIndexJson",
                table: "Datasets",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "DataProfilingReportsIndexJson",
                table: "Datasets",
                type: "nvarchar(max)",
                nullable: true);
        }
    }
}
