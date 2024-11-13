import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="Script to generate prompts for LLM which creates and edits the notes.")
parser.add_argument("-p", "--path_to_datasets", type=str, required=True, help="Path to the datasets folder.")

def create_instructions_prompt(csv_files_paths):
    def get_string(csv_files_names):
        csv_files_count = len(csv_files_names)
        if csv_files_count == 1:
            return f"1 table: {csv_files_names[0]}"
        else:
            tmp = ", ".join(csv_files_names)
            return f"{csv_files_count} tables: {tmp}"
    csv_files_names = [csv_file_path.name for csv_file_path in csv_files_paths]
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
    datasets_folder_path = Path(args.path_to_datasets)
    csv_files_paths = list(datasets_folder_path.glob("*.csv"))

    prompt = create_instructions_prompt(csv_files_paths)

    # TODO Remove writing prompts to file
    with open("GENERATED_NOTES_LLM_PROMPTS.md", "w", encoding="utf-8") as file:
        file.write(f"```\n{prompt}\n```\n")

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
