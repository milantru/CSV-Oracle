import json
import chromadb
import re
from pathlib import Path
from llama_index.llms.ollama import Ollama
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine
from concurrent.futures import ThreadPoolExecutor
from llama_index.vector_stores.chroma import ChromaVectorStore

CHROMA_DB_FOLDER_PATH = str(Path(__file__).parent / Path("../Data/chroma_db"))

def read_file(file_path, load_as_json=False):
    with open(file_path, "r") as f:
        file_content = json.load(f) if load_as_json else f.read()
    return file_content

def create_individual_query_engine_tools(collection_names, db, llm, embedding_model, return_direct=False, dataset_knowledge=None):
    tool_metadata_provider = {
        "csvFiles": ToolMetadata(
            name="csv_files",
            description=(
                "Provides access to the raw dataset in CSV format. "
                "This tool is useful when you want to access actual values from the dataset. "
                "Input to this tool should be a question or a command. It does not have to be concise, provide as much context as possible. "
                "Do not use this tool for retrieval of the column names, if you want to retrieve column names, use tool 'datasetKnowledge' instead."
            ),
            return_direct=return_direct
        ),
        "reports": ToolMetadata(
            name="data_profiling_reports",
            description=(
                "Provides data profiling reports generated from the CSV files. "
                "Use this tool to access statistics such as distributions, averages, minimum/maximum values, "
                "standard deviation, missing values count, unique value counts, and correlations. "
                "Best for understanding overall data quality and statistical patterns. "
                "Input to this tool should be a question or a command. It does not have to be concise, provide as much context as possible."
            ),
            return_direct=return_direct
        ),
        "schema": ToolMetadata(
            name="csv_schema",
            description=(
                "Provides access to the CSVW (CSV on the Web) schema describing the structure of the dataset. "
                "Use this tool to understand column definitions, data types, constraints, relationships, and metadata. "
                "Best suited for schema-related or structural questions. "
                "Input to this tool should be a question or a command. It does not have to be concise, provide as much context as possible."
            ),
            return_direct=return_direct
        ),
        "datasetKnowledge": ToolMetadata(
            name="dataset_knowledge",
            description=(
                "Provides access to the dataset knowledge. It may contain dataset description, descriptions of tables, column descriptions, descriptions of columns correlation etc. "
                "This should be the first place to look when searching for some information about the dataset, unless you are 100% sure you should look somewhere else, for example if you want statistical data like average value in some column, you should use 'reports' tool instead. "
                "You can also use this tool to retrieve column names. "
                "Input to this tool should be a question or a command. It does not have to be concise, provide as much context as possible."
            ),
            return_direct=return_direct
        )
    }

    def create_query_engine_tool(collection_name):
        # collection name should have format "{user_id}-{database_id}-{collection_type}"
        collection_type = collection_name.split("-")[2]
        return QueryEngineTool(
            query_engine=load_index_from_chroma_db(collection_name, db, embedding_model=embedding_model).as_query_engine(llm=llm), # similarity_top_k=1
            metadata=tool_metadata_provider[collection_type]
        )

    with ThreadPoolExecutor() as executor:
        query_engine_tools = list(executor.map(create_query_engine_tool, collection_names))

    if not dataset_knowledge:
        return query_engine_tools
    
    # Also create and add dataset knowledge tool 
    # remove lines containing only formatting, we just format and make each line an embedding,
    # this is part of the code from https://docs.llamaindex.ai/en/stable/api_reference/readers/json/
    json_output = json.dumps(dataset_knowledge.to_dict(), indent=0, ensure_ascii=False)
    lines = json_output.split("\n")
    useful_lines = [line for line in lines if not re.match(r"^[{}\[\],]*$", line)]
    documents = [Document(text="\n".join(useful_lines), metadata={})]
    index = VectorStoreIndex.from_documents(documents, embed_model=embedding_model)
    dataset_knowledge_tool = QueryEngineTool(
        query_engine=index.as_query_engine(llm=llm), # similarity_top_k=1
        metadata=tool_metadata_provider["datasetKnowledge"]
    )
    
    return query_engine_tools + [dataset_knowledge_tool]

def create_sub_question_query_engine(query_engine_tools, llm):
    sub_question_query_engine = SubQuestionQueryEngine.from_defaults(
        query_engine_tools=query_engine_tools,
        llm=llm,
        verbose=False,
        use_async=True
    )

    return sub_question_query_engine

def get_model(model: str, system_prompt: str | None = None, api_key: str | None = None):
    """ATTENTION! For some reason the system prompt is not working when LLM.complete() is used.
    The possible solution for it is to prepend the system prompt at the beginning of the message later when using model.
    """
    if model == "mistral:latest" or model == "qwen2.5:14b" or model == "llama3.2:latest" or model == "llama3.3:latest":
        return Ollama(
            model=model,
            system_prompt=system_prompt,
            request_timeout=420.0
        )
    elif model == "llama-3.3-70b-versatile" or model == "llama-3.3-70b-specdec" or model == "llama3-70b-8192":
        if not api_key:
            raise Exception("Api key required.")
        return Groq(
            model=model,
            system_prompt=system_prompt,
            request_timeout=420.0,
            api_key=api_key
        )
    else:
        raise Exception("Unknown model required.")

def get_embedding_model():
    return HuggingFaceEmbedding()

def get_chroma_db_client():
    return chromadb.PersistentClient(path=CHROMA_DB_FOLDER_PATH)

def load_index_from_chroma_db(collection_name, db, embedding_model):
    chroma_collection = db.get_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=embedding_model,
    )

    return index

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

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "missingValuesExplanation": self.missing_values_explanation,
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.name = data["name"]
        obj.description = data["description"]
        obj.missing_values_explanation = data["missingValuesExplanation"]
        return obj

class Row:
    def __init__(self):
        self.values = []

    def to_dict(self):
        return {
            "values": self.values,
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.values = data["values"]
        return obj

class TableKnowledge:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.row_entity_description = ""
        self.sample_head = []
        self.sample_tail = []
        self.column_knowledges = []
        self.correlation_explanations = []

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "rowEntityDescription": self.row_entity_description,
            "sampleHead": [row.to_dict() for row in self.sample_head],
            "sampleTail": [row.to_dict() for row in self.sample_tail],
            "columnKnowledges": [ck.to_dict() for ck in self.column_knowledges],
            "correlationExplanations": [ce.to_dict() for ce in self.correlation_explanations]
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls()
        obj.name = data["name"]
        obj.description = data["description"]
        obj.row_entity_description = data["rowEntityDescription"]
        obj.sample_head = [Row.from_dict(row) for row in data["sampleHead"]]
        obj.sample_tail = [Row.from_dict(row) for row in data["sampleTail"]]
        obj.column_knowledges = [ColumnKnowledge.from_dict(ck) for ck in data["columnKnowledges"]]
        obj.correlation_explanations = [CorrelationExplanation.from_dict(ce) for ce in data["correlationExplanations"]]
        return obj

class DatasetKnowledge:
    def __init__(self):
        self.description = ""
        self.table_knowledges = []

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
