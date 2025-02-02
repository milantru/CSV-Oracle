import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="Script for generating Notes LLM instructions prompt.")
parser.add_argument("-i", "--input_csv_files_folder_path", type=str, required=True, help="Path to the folder containing csv files of the dataset.")
parser.add_argument("-o", "--output_file_path", type=str, required=True, help="Path to the file where the instructions for the Notes LLM should be written. The new file will be created, or overwritten if already exists.")

def create_instructions_prompt(csv_file_names):
    def get_table_object_string(csv_file_name):
        return f"""\
{{
        "name": "{csv_file_name}",
        "description": "{csv_file_name} DESCRIPTION",
        "columns": [
            {{
                "name": "COLUMN_1 NAME",
                "description": "COLUMN_1 DESCRIPTION"
            }},
            {{
                "name": "COLUMN_2 NAME",
                "description": "COLUMN_2 DESCRIPTION"
            }},
            ...
        ]
}}\
"""
    
    table_object_strings = ",\n".join([get_table_object_string(csv_file_name) for csv_file_name in csv_file_names])
    return f'''\
INSTRUCTIONS:
- The dataset knowledge is JSON containing information about the dataset following this template:
```json
{{
    "tables": [
        {table_object_strings}
        ...
    ],
    "implementation_details": "OPTIONAL IMPLEMENTATION DETAILS"
}}
```
- You will be given current dataset knowledge and instruction section.
- Your task is to maintain the dataset knowledge based on the instructions provided in instruction section.
- The dataset knowledge must follow the provided template, however new optional keys and values can be added or removed, but the keys mentioned in the template are REQUIRED and MUST be present.
- *When responding*:
    - Always reply with the updated version of the dataset knowledge in JSON format (the entire JSON, not just a part of it).
    - Do **NOT** include any additional text apart from the JSON, for example like heading "Updated version of the dataset knowledge", of summary footing, or sentences like "Details for this table will be added later" or similar.
    - Output only JSON in provided format, no other text, it is IMPORTANT!
- *Column-specific information*: Each column should be described in its own section with relevant details about that column.
    - If information about a specific column appears, add it to the section of the corresponding column.
- The values under "tables" key should contain information related to the dataset. If some implementation details information (such as tools, libraries, or code snippets) required to work with the dataset occur, it should be placed in the values under the "implementation_details" key.
- *General guidelines*:
    - The notes should **ONLY** include provided information.
    - **Do not** speculate or include information that has not been explicitly provided.
    - The notes should **evolve over time** as new information is provided.
    - All content should be written in **English**, as the software engineers are expected to speak English. But you can remain the names (e.g. column names) in original language unless the user specifically asked to change it.\
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
