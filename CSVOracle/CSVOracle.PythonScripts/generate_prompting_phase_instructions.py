import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="Script for generating prompting phase instructions prompt.")
parser.add_argument("-i", "--input_csv_files_folder_path", type=str, required=True, help="Path to the folder containing csv files of the dataset.")
parser.add_argument("-o", "--output_file_path", type=str, required=True, help="Path to the file where the instructions should be written. The new file will be created, or overwritten if already exists.")

def create_instructions_prompt(csv_files_names):
    def get_string(csv_files_names):
        csv_files_count = len(csv_files_names)
        if csv_files_count == 1:
            return f"1 table: {csv_files_names[0]}"
        else:
            tmp = ", ".join(csv_files_names)
            return f"{csv_files_count} tables: {tmp}"
    return f'''\
INSTRUCTIONS:
- You function as a tool for software engineers to answer questions about the dataset.
- First you will be given information about the dataset. Information like sample data and possibly schema, additional information about the dataset, user view, or output from data profiling.
- Then you will be prompted with questions about the dataset and you will answer them, aiming to extract as much information as possible.
- Your answers should be concise and to the point, containing only the answer to the question. So no other text, like for example "Feel free to ask me if you have more questions...".
- The dataset consists of {get_string(csv_files_names)}.
- The language of the dataset may differ from that of the user, who is expected to speak English. Because of that, you will answer questions about the dataset in English by default.
'''

def main(args):
    csv_files_folder_path = Path(args.input_csv_files_folder_path)
    csv_files_paths = list(csv_files_folder_path.glob("*.csv"))
    csv_files_names = [csv_file_path.name for csv_file_path in csv_files_paths]

    prompt = create_instructions_prompt(csv_files_names)

    with open(args.output_file_path, "w") as file:
        file.write(prompt)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
