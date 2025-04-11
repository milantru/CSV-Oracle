import argparse
from shared_helpers import get_chroma_db_client

parser = argparse.ArgumentParser(description="Script for deleting Chroma DB collections.")
parser.add_argument("-c", "--collection_names", type=str, required=True, help="Chroma DB collection names to be deleted.")

def main(args):
    db = get_chroma_db_client()
    for collection_name in args.collection_names:
        db.delete_collection(collection_name)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
