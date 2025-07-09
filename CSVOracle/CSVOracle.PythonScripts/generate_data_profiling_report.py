import json
import argparse
import pandas as pd
from pathlib import Path
from ydata_profiling import ProfileReport
from ydata_profiling.config import Settings

parser = argparse.ArgumentParser(description="Script for generating a data profiling report of the csv file.")
parser.add_argument("-i", "--input_csv_file_path", type=str, required=True, help="Path to the csv file of the dataset.")
parser.add_argument("-m", "--metadata_file_path", type=str, required=True, help="Path to the file containing dataset metadata.")
parser.add_argument(
    "-o", "--output_folder_path", type=str, required=True, 
    help=(
        "Path to the folder where the report should be stored. The new file with the same name as the input file "
        "(but with the '_report' and extension .json) will be created, or overwritten if already exists."
    )
)

def create_data_profiling_report(csv_file_path, separator, encoding):
    df = pd.read_csv(csv_file_path, sep=separator, encoding=encoding)

    report = ProfileReport(
        df=df,
        title="CSV Oracle dataset profiling report using ydata profiling",
        config=Settings(progress_bar=False)
    )

    return report

def read_dataset_metadata_file(metadata_file_path):
    with open(metadata_file_path, "r") as file:
        metadata = json.load(file)

    return metadata["separator"], metadata["encoding"]

def main(args: argparse.Namespace):
    """
    Generate and save a data profiling report for a CSV file.

    Args:
        args (argparse.Namespace): Command-line arguments.
    """
    separator, encoding = read_dataset_metadata_file(args.metadata_file_path)
    csv_file_path = Path(args.input_csv_file_path)

    report = create_data_profiling_report(csv_file_path, separator, encoding)

    report_file_path = Path(args.output_folder_path) / f"{csv_file_path.stem}_report.json"
    report.to_file(report_file_path)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
