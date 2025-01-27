import argparse
import pandas as pd
from ydata_profiling import ProfileReport
from pathlib import Path
from shared_helpers import read_dataset_metadata_file

parser = argparse.ArgumentParser(description="Script for generating a data profiling report of the csv file.")
parser.add_argument("-i", "--input_csv_file_path", type=str, required=True, help="Path to the csv file of the dataset.")
parser.add_argument("-m", "--metadata_file_path", type=str, required=True, help="Path to the file containing dataset metadata.")
parser.add_argument("-o", "--output_folder_path", type=str, required=True, help="Path to the folder where the report should be stored. The new file with the same name as the input file (but with the '_report' and extension .json) will be created, or overwritten if already exists.")

def create_data_profiling_report(csv_file_path, separator, encoding):
    df = pd.read_csv(csv_file_path, sep=separator, encoding=encoding)

    type_schema = None # {"Survived": "categorical", "Embarked": "categorical"} # TODO (schema) Schema?
    report = ProfileReport(df, title="CSV Oracle profiling report using ydata profiling", type_schema=type_schema)

    return report

def main(args):
    _, separator, encoding = read_dataset_metadata_file(args.metadata_file_path)
    csv_file_path = Path(args.input_csv_file_path)

    report = create_data_profiling_report(csv_file_path, separator, encoding)

    report_file_path = Path(args.output_folder_path) / f"{csv_file_path.stem}_report.json"
    report.to_file(report_file_path)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
