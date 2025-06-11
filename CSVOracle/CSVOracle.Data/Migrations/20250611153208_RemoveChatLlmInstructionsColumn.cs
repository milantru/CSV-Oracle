using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace CSVOracle.Data.Migrations
{
    /// <inheritdoc />
    public partial class RemoveChatLlmInstructionsColumn : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "ChatLlmInstructions",
                table: "Datasets");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "ChatLlmInstructions",
                table: "Datasets",
                type: "nvarchar(max)",
                nullable: true);
        }
    }
}
