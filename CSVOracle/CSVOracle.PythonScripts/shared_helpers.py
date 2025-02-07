import json
import re
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext, load_index_from_storage

def get_embedding_model():
    return HuggingFaceEmbedding()

def create_notes_llm(notes_llm_instructions=None):
    return Ollama(
        model="deepseek-r1:8b", 
        request_timeout=420.0, 
        # For some reason the system prompt is not working when LLM.complete() is used. That is why 
        # I prepend instructions (system prompt) at the beginning of the prompt later when using Notes LLM.
        # system_prompt=notes_llm_instructions
    )

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

def create_notes_llm_prompt(dataset_knowledge, instruction):
    return f"""\
CURRENT DATASET KNOWLEDGE:
```json
{dataset_knowledge}
```

INSTRUCTION SECTION:
{instruction}
"""

def create_updated_dataset_knowledge(notes_llm, notes_llm_prompt, max_attempts_count = 3, json_regex=re.compile(r'```json([\s\S]*?)```')):
    attempts_count = 0
    while attempts_count < max_attempts_count:
        try:
            res = notes_llm.complete(notes_llm_prompt)
            res_json = _extract_json_part(json_regex, str(res))
            if not res_json: raise Exception("JSON part not extracted.")
            dataset_knowledge = json.loads(res_json)
            break
        except:
            print(f"Failed creating updated dataset knowledge.")
            attempts_count += 1
            if attempts_count < max_attempts_count:
                print("Retrying...")
            else: 
                print(f"Failed creating updated dataset knowledge for Notes LLM prompt:\n'{notes_llm_prompt}'.")
                return None
    return dataset_knowledge
