﻿// <auto-generated />
using CSVOracle.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Metadata;
using Microsoft.EntityFrameworkCore.Storage.ValueConversion;

#nullable disable

namespace CSVOracle.Data.Migrations
{
    [DbContext(typeof(CSVOracleDbContext))]
    partial class CSVOracleDbContextModelSnapshot : ModelSnapshot
    {
        protected override void BuildModel(ModelBuilder modelBuilder)
        {
#pragma warning disable 612, 618
            modelBuilder
                .HasAnnotation("ProductVersion", "8.0.12")
                .HasAnnotation("Relational:MaxIdentifierLength", 128);

            SqlServerModelBuilderExtensions.UseIdentityColumns(modelBuilder);

            modelBuilder.Entity("CSVOracle.Data.Models.Chat", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("int");

                    SqlServerPropertyBuilderExtensions.UseIdentityColumn(b.Property<int>("Id"));

                    b.Property<string>("CurrentDatasetKnowledgeJson")
                        .IsRequired()
                        .HasColumnType("nvarchar(max)");

                    b.Property<int>("DatasetId")
                        .HasColumnType("int");

                    b.Property<string>("MessagesJson")
                        .IsRequired()
                        .HasColumnType("nvarchar(max)");

                    b.Property<int>("Name")
                        .HasColumnType("int");

                    b.Property<string>("UserView")
                        .IsRequired()
                        .HasColumnType("nvarchar(max)");

                    b.HasKey("Id");

                    b.HasIndex("DatasetId");

                    b.ToTable("Chats");
                });

            modelBuilder.Entity("CSVOracle.Data.Models.Dataset", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("int");

                    SqlServerPropertyBuilderExtensions.UseIdentityColumn(b.Property<int>("Id"));

                    b.Property<string>("AdditionalInfoIndexJson")
                        .HasColumnType("nvarchar(max)");

                    b.Property<string>("ChatLlmInstructions")
                        .HasColumnType("nvarchar(max)");

                    b.Property<string>("Encoding")
                        .HasColumnType("nvarchar(max)");

                    b.Property<string>("FirstChatMessage")
                        .HasColumnType("nvarchar(max)");

                    b.Property<string>("InitialDatasetKnowledgeJson")
                        .HasColumnType("nvarchar(max)");

                    b.Property<string>("NotesLlmInstructions")
                        .HasColumnType("nvarchar(max)");

                    b.Property<string>("Separator")
                        .HasColumnType("nvarchar(1)");

                    b.Property<int>("State")
                        .HasColumnType("int");

                    b.Property<int>("UserId")
                        .HasColumnType("int");

                    b.HasKey("Id");

                    b.HasIndex("UserId");

                    b.ToTable("Datasets");
                });

            modelBuilder.Entity("CSVOracle.Data.Models.DatasetFile", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("int");

                    SqlServerPropertyBuilderExtensions.UseIdentityColumn(b.Property<int>("Id"));

                    b.Property<string>("CsvFileIndexJson")
                        .IsRequired()
                        .HasColumnType("nvarchar(max)");

                    b.Property<string>("DataProfilingIndexJson")
                        .IsRequired()
                        .HasColumnType("nvarchar(max)");

                    b.Property<int>("DatasetId")
                        .HasColumnType("int");

                    b.HasKey("Id");

                    b.HasIndex("DatasetId");

                    b.ToTable("DatasetFiles");
                });

            modelBuilder.Entity("CSVOracle.Data.Models.User", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("int");

                    SqlServerPropertyBuilderExtensions.UseIdentityColumn(b.Property<int>("Id"));

                    b.Property<string>("Email")
                        .IsRequired()
                        .HasColumnType("nvarchar(max)");

                    b.Property<string>("Password")
                        .IsRequired()
                        .HasColumnType("nvarchar(max)");

                    b.HasKey("Id");

                    b.ToTable("Users");
                });

            modelBuilder.Entity("CSVOracle.Data.Models.Chat", b =>
                {
                    b.HasOne("CSVOracle.Data.Models.Dataset", "Dataset")
                        .WithMany("Chats")
                        .HasForeignKey("DatasetId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Dataset");
                });

            modelBuilder.Entity("CSVOracle.Data.Models.Dataset", b =>
                {
                    b.HasOne("CSVOracle.Data.Models.User", "User")
                        .WithMany("Datasets")
                        .HasForeignKey("UserId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("User");
                });

            modelBuilder.Entity("CSVOracle.Data.Models.DatasetFile", b =>
                {
                    b.HasOne("CSVOracle.Data.Models.Dataset", "Dataset")
                        .WithMany("DatasetFiles")
                        .HasForeignKey("DatasetId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Dataset");
                });

            modelBuilder.Entity("CSVOracle.Data.Models.Dataset", b =>
                {
                    b.Navigation("Chats");

                    b.Navigation("DatasetFiles");
                });

            modelBuilder.Entity("CSVOracle.Data.Models.User", b =>
                {
                    b.Navigation("Datasets");
                });
#pragma warning restore 612, 618
        }
    }
}