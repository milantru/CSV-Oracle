import argparse
from pathlib import Path
from llama_index.core import VectorStoreIndex
from llama_index.readers.file import CSVReader
from llama_index.readers.json import JSONReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from shared_helpers import get_embedding_model, get_chroma_db_client

parser = argparse.ArgumentParser(description=(
    "Script for creating and storing index in Chroma DB collection either from .txt, .csv, or .json file(s). "
    "If input is a folder, it cannot be empty and all files must share the same extension."
))
parser.add_argument(
    "-i", "--input_path", type=str, required=True, 
    help="Path to the input file or non-empty folder containing input files sharing the same extension."
)
parser.add_argument(
    "-c", "--collection_name", type=str, required=True, 
    help="Name of the ChromaDB collection where index will be stored."
)

def get_file_paths(folder_path):
    return [file_path for file_path in folder_path.iterdir() if file_path.is_file()]

def get_documents(files_paths: list[Path]):
    extension = files_paths[0].suffix
    if extension == ".csv":
        csv_reader = CSVReader()
        documents = []
        for file_path in files_paths:
            csv_docs = csv_reader.load_data(file=file_path)
            if len(csv_docs) > 1:
                print("Warning: number of csv file docs is more than 1.")
            for i, doc in enumerate(csv_docs):
                table_name = file_path.stem
                doc.metadata["table_name"] = table_name
            documents.extend(csv_docs)
    elif extension == ".json":
        json_reader = JSONReader()
        documents = []
        for file_path in files_paths:
            json_docs = json_reader.load_data(input_file=file_path)
            if len(json_docs) > 1:
                print("Warning: number of report docs is more than 1.")
            for doc in json_docs:
                table_name = file_path.stem.removesuffix("_report")
                doc.metadata["table_name"] = table_name
            documents.extend(json_docs)
    else:
        raise ValueError("Unsupported file extension. Only .txt, .csv, and .json are supported.")
    
    return documents

def main(args: argparse.Namespace):
    """
    Create and store a vector index in a ChromaDB collection from input file(s).

    Args:
        args (argparse.Namespace): Command-line arguments.
    """
    # Setup
    input_path = Path(args.input_path)
    files_paths = [input_path] if input_path.is_file() else get_file_paths(input_path)

    db = get_chroma_db_client()
    print("Creating collection ", args.collection_name)
    chroma_collection = db.create_collection(args.collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    print("Created collection ", args.collection_name)
    
    # Load documents
    documents = get_documents(files_paths)

    # Save index to Chroma DB
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, embed_model=get_embedding_model()
    )

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
