using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace CSVOracle.Data.Migrations
{
    /// <inheritdoc />
    public partial class UpdateChatEntity : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "FirstChatMessage",
                table: "Chats");

            migrationBuilder.RenameColumn(
                name: "MessagesJson",
                table: "Chats",
                newName: "ChatHistoryJson");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.RenameColumn(
                name: "ChatHistoryJson",
                table: "Chats",
                newName: "MessagesJson");

            migrationBuilder.AddColumn<string>(
                name: "FirstChatMessage",
                table: "Chats",
                type: "nvarchar(max)",
                nullable: false,
                defaultValue: "");
        }
    }
}
