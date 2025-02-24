import json
import re
from llama_index.llms.ollama import Ollama
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from concurrent.futures import ThreadPoolExecutor
import time
from pathlib import Path

def checkpoint(prev_time: float, msg: str = None):
    curr_time = time.time()
    if msg:
        print(msg)
    print(f"Elapsed time: {curr_time - prev_time:.6f} seconds")
    return time.time()

def get_model(model: str, system_prompt: str | None = None, api_key: str | None = None):
    """ATTENTION! For some reason the system prompt is not working when LLM.complete() is used.
    The possible solution for it is to prepend the system prompt at the beginning of the message later when using model.
    """
    if model == "mistral:latest" or model == "qwen2.5:14b" or model == "llama3.2:latest":
        return Ollama(
            model=model, 
            system_prompt=system_prompt
        )
    elif model == "llama-3.3-70b-versatile" or model == "llama-3.3-70b-specdec":
        if not api_key:
            raise Exception("Api key required.")
        return Groq(
            model=model, 
            api_key=api_key
        )
    elif model == "deepseek-r1:8b":
        return  Ollama(
            model=model, 
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

def load_index(index_storage_context_dict_path, embedding_model):
    with open(index_storage_context_dict_path, "r") as index_storage_context_dict_file:
        index_storage_context_dict = json.load(index_storage_context_dict_file)
    index_storage_context = StorageContext.from_dict(index_storage_context_dict)
    index = load_index_from_storage(index_storage_context, embed_model=embedding_model)
    return index

def create_individual_query_engine_tools(index_storage_context_dicts_paths, llm, embedding_model):
    tool_metadata_provider = {
        "additional_info_index.json": ToolMetadata(
            name="additional_dataset_information",
            description=(
                "Provides text with additional information about the dataset provided by the user."
                "Use a detailed plain text question as input to the tool."
            ),
            return_direct=True
        ),
        "csv_files_index.json": ToolMetadata(
            name="csv_files",
            description=(
                "Provides actual dataset (all CSV files)."
                "Useful for when you want to access raw data of the dataset."
                "Use a detailed plain text question as input to the tool."
            ),
            return_direct=True
        ),
        "reports_index.json": ToolMetadata(
            name="data_profiling_reports",
            description=(
                "Provides reports generated from data profiling of csv files."
                "Use a detailed plain text question as input to the tool."
            ),
            return_direct=True
        ),
    }

    def create_query_engine_tool(path: Path):
        return QueryEngineTool(
            query_engine=load_index(path, embedding_model).as_query_engine(llm=llm),
            metadata=tool_metadata_provider[Path(path).name]
        )

    with ThreadPoolExecutor() as executor:
        query_engine_tools = list(executor.map(create_query_engine_tool, index_storage_context_dicts_paths))

    return query_engine_tools

class CorrelationExplanation:
    def __init__(self):
        self.column1_name = ""
        self.column2_name = ""
        self.correlation_value = ""
        self.explanation = ""

    def to_dict(self):
        return {
            "column1Name": self.column1_name,
            "column2Name": self.column2_name,
            "correlationValue": self.correlation_value,
            "explanation": self.explanation
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.column1_name = data["column1Name"]
        obj.column2_name = data["column2Name"]
        obj.correlation_value = data["correlationValue"]
        obj.explanation = data["explanation"]
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
            "missingValuesExplanation": self.missing_values_explanation,
            "correlationExplanations": [ce.to_dict() for ce in self.correlation_explanations]
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.name = data["name"]
        obj.description = data["description"]
        obj.missing_values_explanation = data["missingValuesExplanation"]
        obj.correlation_explanations = [CorrelationExplanation.from_dict(ce) for ce in data["correlationExplanations"]]
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
            "rowEntityDescription": self.row_entity_description,
            "columnKnowledges": [ck.to_dict() for ck in self.column_knowledges]
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.name = data["name"]
        obj.description = data["description"]
        obj.row_entity_description = data["rowEntityDescription"]
        obj.column_knowledges = [ColumnKnowledge.from_dict(ck) for ck in data["columnKnowledges"]]
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
            "tableKnowledges": [tk.to_dict() for tk in self.table_knowledges],
            # "other": self.other
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.description = data["description"]
        obj.table_knowledges = [TableKnowledge.from_dict(tk) for tk in data["tableKnowledges"]]
        # obj.other = data["other"]
        return obj
