import json

def read_dataset_metadata_file(metadata_file_path):
    with open(metadata_file_path, 'r') as file:
        metadata = json.load(file)

    return metadata["additionalInfo"], metadata["separator"], metadata["encoding"]
