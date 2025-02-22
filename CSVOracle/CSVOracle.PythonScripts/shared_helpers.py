import json
import re
from llama_index.llms.ollama import Ollama
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext, load_index_from_storage

def get_model(model: str, system_prompt: str | None = None, api_key: str | None = None):
    """ATTENTION! For some reason the system prompt is not working when LLM.complete() is used.
    The possible solution for it is to prepend the system prompt at the beginning of the message later when using model.
    """
    if model == "mistral:latest" or model == "qwen2.5:14b" or model == "llama3.2:latest":
        return Ollama(
            model=model, 
            system_prompt=system_prompt
        )
    elif model == "llama-3.3-70b-versatile":
        if not api_key:
            raise Exception("Api key required.")
        return Groq(
            model="llama-3.3-70b-versatile", 
            api_key=api_key
        )
    elif model == "deepseek-r1:8b":
        return  Ollama(
            model="deepseek-r1:8b", 
            system_prompt=system_prompt, 
            request_timeout=420.0, 
            is_function_calling_model=False
        )
    else:
        raise Exception("Unknown model required.")

def get_embedding_model():
    return HuggingFaceEmbedding()

def read_dataset_metadata_file(metadata_file_path):
    with open(metadata_file_path, 'r') as file:
        metadata = json.load(file)

    return metadata["additionalInfo"], metadata["separator"], metadata["encoding"]

def get_file_paths(folder_path):
    return [file_path for file_path in folder_path.iterdir() if file_path.is_file()]

def read_file(file_path, load_as_json=False):
    with open(file_path, "r") as f:
        file_content = json.load(f) if load_as_json else f.read()
    return file_content

def load_index(index_storage_context_dict_path):
    with open(index_storage_context_dict_path, "r") as index_storage_context_dict_file:
        index_storage_context_dict = json.load(index_storage_context_dict_file)
    index_storage_context = StorageContext.from_dict(index_storage_context_dict)
    index = load_index_from_storage(index_storage_context, embed_model=get_embedding_model())
    return index

def _extract_json_part(json_regex, text):
    think_end_tag_index = text.find("</think>")
    if think_end_tag_index != -1:
        text = text[think_end_tag_index + len("</think>"):].lstrip()

    match = json_regex.search(text)
    if not match:
        return None
    tmp = match.group(1)
    if tmp.startswith("```json\n"):
        tmp = tmp[8:]
    elif tmp.startswith("```json"):
        tmp = tmp[7:]
    if tmp.endswith("\n```"):
        tmp = tmp[:-4]
    elif tmp.endswith("```"):
        tmp = tmp[:-4]

    return tmp

# TODO move to the file where it is used (i think its no more shared)
def create_notes_llm_prompt(dataset_knowledge, instruction):
    return f"""\
CURRENT DATASET KNOWLEDGE:
```json
{dataset_knowledge}
```

INSTRUCTION SECTION:
{instruction}
"""

class CorrelationExplanation:
    def __init__(self):
        self.column1_name = ""
        self.column2_name = ""
        self.correlation_value = ""
        self.explanation = ""

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.__dict__.update(data)
        return obj

class ColumnKnowledge:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.missing_values_explanation = ""
        self.correlation_explanations = []

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "missing_values_explanation": self.missing_values_explanation,
            "correlation_explanations": [ce.to_dict() for ce in self.correlation_explanations]
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.name = data["name"]
        obj.description = data["description"]
        obj.missing_values_explanation = data["missing_values_explanation"]
        obj.correlation_explanations = [CorrelationExplanation.from_dict(ce) for ce in data["correlation_explanations"]]
        return obj

class TableKnowledge:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.row_entity_description = ""
        self.column_knowledges = []

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "row_entity_description": self.row_entity_description,
            "column_knowledges": [ck.to_dict() for ck in self.column_knowledges]
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.name = data["name"]
        obj.description = data["description"]
        obj.row_entity_description = data["row_entity_description"]
        obj.column_knowledges = [ColumnKnowledge.from_dict(ck) for ck in data["column_knowledges"]]
        return obj

class DatasetKnowledge:
    def __init__(self):
        self.description = ""
        self.table_knowledges = []
        # TODO might add "other" (not only to dataset knowledge)
        # self.other = "" # Reserved for other info, e.g. info about frameworks that can be used for work with dataset

    def to_dict(self):
        return {
            "description": self.description,
            "table_knowledges": [tk.to_dict() for tk in self.table_knowledges],
            # "other": self.other
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.description = data["description"]
        obj.table_knowledges = [TableKnowledge.from_dict(tk) for tk in data["table_knowledges"]]
        # obj.other = data["other"]
        return obj
