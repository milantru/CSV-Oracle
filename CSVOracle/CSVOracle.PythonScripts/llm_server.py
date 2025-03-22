from generate_answer import main
from flask import Flask, request
import json

class Args:
    def __init__(self, **entries):
        self.__dict__.update(entries)

app = Flask(__name__)

@app.route("/generate-answer", methods=["POST"])
def generate_answer():
    data = request.get_json()

    args = Args(**{
        "indices_folder_path": data.get("indices_folder_path"),
        "dataset_knowledge_path": data.get("dataset_knowledge_path"),
        "user_view_path": data.get("user_view_path", None),
        "chat_history_path": data.get("chat_history_path", None),
        "message_path": data.get("message_path"),
        "updated_chat_history_path": data.get("updated_chat_history_path"),
        "updated_dataset_knowledge_path": data.get("updated_dataset_knowledge_path"),
        "answer_path": data.get("answer_path"),
        "api_keys": json.loads(data.get("api_keys")),
    })

    try:
        main(args)
        return "Answer generated successfully", 200
    except:
        return "Failed to generate answer", 500

print("LLM server is running")
