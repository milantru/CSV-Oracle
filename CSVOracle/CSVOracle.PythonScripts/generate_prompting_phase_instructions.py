import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="Script for generating prompting phase instructions prompt.")
parser.add_argument(
    "-i", "--input_csv_files_folder_path", type=str, required=True, 
    help="Path to the folder containing csv files of the dataset."
)
parser.add_argument(
    "-o", "--output_file_path", type=str, required=True, 
    help=(
        "Path to the file where the instructions should be written. "
        "The new file will be created, or overwritten if already exists."
    )
)

def create_instructions_prompt(csv_files_names):
    def get_string(csv_files_names):
        csv_files_count = len(csv_files_names)
        if csv_files_count == 1:
            return f"1 table: {csv_files_names[0]}. So when talking about the dataset, we are talking about this table"
        else:
            tmp = ", ".join(csv_files_names)
            return f"{csv_files_count} tables: {tmp}"
    return f'''\
INSTRUCTIONS:
- You are a language model assistant designed to analyze datasets for software engineers and data analysts.
- The dataset consists of {get_string(csv_files_names)}.
- You will be prompted with questions about the dataset. Answer these questions as accurately and thoroughly as possible.
- Your responses must be in plain text only. Do not use Markdown formatting such as bold text, or code blocks.
- Your responses should be concise and direct, containing only the answer to the question. Do not include greetings, follow-up offers, or meta-commentary.
- Even if the dataset is in another language, always respond in English.
- You can use the original column names, even if they're in a language other than English, but don't expect users to understand them. Always assume the user speaks only English.
- You can output the names of the files, but not the full paths.
- You must only use the information provided. Do not make up any facts. If the information is missing or unclear, answer best you can, but do not hallucinate.
'''

def main(args: argparse.Namespace):
    """
    Generate and save a prompting phase instructions prompt based on CSV files in a folder.

    Args:
        args (argparse.Namespace): Command-line arguments.
    """
    csv_files_folder_path = Path(args.input_csv_files_folder_path)
    csv_files_paths = list(csv_files_folder_path.glob("*.csv"))
    csv_files_names = [csv_file_path.name for csv_file_path in csv_files_paths]

    prompt = create_instructions_prompt(csv_files_names)

    with open(args.output_file_path, "w") as file:
        file.write(prompt)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
