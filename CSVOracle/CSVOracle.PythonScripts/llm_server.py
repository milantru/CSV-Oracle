from generate_answer import main as generate_answer_main
from delete_collections import main as delete_collections_main
from flask import Flask, request
import json

class Args:
    def __init__(self, **entries):
        self.__dict__.update(entries)

app = Flask(__name__)

@app.route("/generate-answer", methods=["POST"])
def generate_answer():
    """
    Endpoint to generate an answer for the user message.
    Calling this endpoint executes the main function of the generate_answer.py script.
    The JSON payload expected from this endpoint matches the arguments for the generate_answer.py script.

    Returns HTTP 200 on success, or HTTP 500 on failure.
    """
    data = request.get_json()

    args = Args(**{
        "collection_names": data.get("collection_names"),
        "dataset_knowledge_path": data.get("dataset_knowledge_path"),
        "user_view_path": data.get("user_view_path", None),
        "chat_history_path": data.get("chat_history_path", None),
        "message_path": data.get("message_path"),
        "updated_chat_history_path": data.get("updated_chat_history_path"),
        "updated_dataset_knowledge_path": data.get("updated_dataset_knowledge_path"),
        "api_keys": json.loads(data.get("api_keys")),
    })

    try:
        generate_answer_main(args)
        return "Answer generated successfully", 200
    except Exception as e:
        print(e)
        return "Failed to generate answer", 500

@app.route("/delete-collections", methods=["POST"])
def delete_collections():
    """
    Endpoint to delete specified collections.
    Calling this endpoint executes the main function of the delete_collections.py script.
    The JSON payload expected from this endpoint matches the arguments for the delete_collections.py script.

    Returns HTTP 200 on success, or HTTP 500 on failure.
    """
    data = request.get_json()

    args = Args(**{
        "collection_names": data.get("collection_names")
    })

    try:
        delete_collections_main(args)
        return "Collections deleted successfully", 200
    except Exception as e:
        print(e)
        return "Failed to delete collections", 500

print("LLM server is running")
