import argparse
import json
from pathlib import Path
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.readers.json import JSONReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

parser = argparse.ArgumentParser(description="Script for generating an index storage context dictionary file from either .txt, .csv, or .json file(s). If input is folder, it cannot be empty and all files must share the same extension.")
parser.add_argument("-i", "--input_path", type=str, required=True, help="Path to the input file or non-empty folder containing input files sharing the same extension.")
parser.add_argument("-o", "--output_file_path", type=str, required=True, help="Path to the file where the index storage context dictionary should be stored. The new file will be created, or overwritten if already exists.")

def get_file_paths(folder_path):
    return [file_path for file_path in folder_path.iterdir() if file_path.is_file()]

def get_documents(files_paths):
    extension = files_paths[0].suffix
    if extension == ".txt" or extension == ".csv":
        return SimpleDirectoryReader(input_files=files_paths).load_data()
    elif extension == ".json":
        json_reader = JSONReader()
        documents = []
        for file_path in files_paths:
            documents.extend(json_reader.load_data(input_file=file_path))
        return documents
    else:
        raise ValueError("Unsupported file extension. Only .txt, .csv, and .json are supported.")

def main(args):
    input_path = Path(args.input_path)
    files_paths = [input_path] if input_path.is_file() else get_file_paths(input_path)
    
    documents = get_documents(files_paths)
    
    index = VectorStoreIndex.from_documents(documents, embed_model=HuggingFaceEmbedding())

    index_storage_context_dict=index.storage_context.to_dict()
    with open(args.output_file_path, 'w') as output_file:
        json.dump(index_storage_context_dict, output_file)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
