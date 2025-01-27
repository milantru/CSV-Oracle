import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="Script for generating Notes LLM instructions prompt.")
parser.add_argument("-i", "--input_csv_files_folder_path", type=str, required=True, help="Path to the folder containing csv files of the dataset.")
parser.add_argument("-o", "--output_file_path", type=str, required=True, help="Path to the file where the instructions for the Notes LLM should be written. The new file will be created, or overwritten if already exists.")

def create_instructions_prompt(csv_files_names):
    def get_string(csv_files_names):
        csv_files_count = len(csv_files_names)
        if csv_files_count == 1:
            return f"1 table: {csv_files_names[0]}"
        else:
            tmp = ", ".join(csv_files_names)
            return f"{csv_files_count} tables: {tmp}"
    return f'''\
**INSTRUCTIONS:**
- Your task is to create and maintain notes for the software engineer about the dataset, which consists of {get_string(csv_files_names)}.
- The user view is: **"I would like to use this dataset for visualization of the population movement."**
- You will receive instructions on how to edit the notes.
- **When responding**:
    - Always reply with the updated version of the notes in **Markdown format** (the entire document, not just a part of it).
    - Do **NOT** include additional text like "Details for this table will be added later" or similar. Only provide the notes document.
- **Column-specific information**: Each column should be described in its own section with relevant details about that column.
    - If information about a specific column appears, add it to the section of the corresponding column.
- The notes should contain information related to the dataset. If some implementation details information (such as tools, libraries, or code snippets) required to work with the dataset occur, it should be clearly separated from dataset information with its own heading.
- **General guidelines**:
    - The notes should **ONLY** include provided information.
    - **Do not** speculate or include information that has not been explicitly provided.
    - The notes should **evolve over time** as new information is provided.
    - All content should be written in **English**, as the software engineers are expected to speak English.

If you understand these instructions, please respond with "OK".\
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
