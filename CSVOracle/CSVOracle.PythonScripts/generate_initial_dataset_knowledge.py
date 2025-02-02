import argparse
import json
import re
from pathlib import Path
from llama_index.core import StorageContext, BasePromptTemplate, load_index_from_storage
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.schema import QueryBundle


parser = argparse.ArgumentParser(description="Script for generating an initial dataset knowledge representation.")
parser.add_argument("-i", "--indices_folder_path", type=str, required=True, help="Path to the input folder containing index files (or to be more precise, index storage context dictionary files).")
parser.add_argument("-p", "--prompting_phase_prompts_path", type=str, required=True, help="Path to the input file containing prompting phase prompts.")
parser.add_argument("-r", "--prompting_phase_instructions_path", type=str, required=True, help="Path to the input file containing prompting phase instructions.")
parser.add_argument("-n", "--notes_llm_instructions_path", type=str, required=True, help="Path to the input file containing Notes LLM instructions prompt.")
parser.add_argument("-o", "--output_file_path", type=str, required=True, help="Path to the file where the initial dataset knowledge representation should be stored. The new file will be created, or overwritten if already exists.")

def get_file_paths(folder_path): # TODO move to shared funcs
    return [file_path for file_path in folder_path.iterdir() if file_path.is_file()]

def read_file(file_path, load_as_json=False): # TODO move to shared funcs
    with open(file_path, "r") as f:
        file_content = json.load(f) if load_as_json else f.read()
    return file_content

def load_index(index_storage_context_dict_path):
    with open(index_storage_context_dict_path, "r") as index_storage_context_dict_file:
        index_storage_context_dict = json.load(index_storage_context_dict_file)
    index_storage_context = StorageContext.from_dict(index_storage_context_dict)
    index = load_index_from_storage(index_storage_context, embed_model=HuggingFaceEmbedding()) # TODO maybe to shared (embed model)?
    return index

def extract_json_part(json_regex, text):
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

def create_notes_llm_prompt(dataset_knowledge, question, answer):
    return f"""\
CURRENT DATASET KNOWLEDGE:
```json
{dataset_knowledge}
```

INSTRUCTION SECTION:
The answer for the question "{question}" was:
"{answer}"

Please, based on the provided answer, add the newly gained information to the CURRENT DATASET KNOWLEDGE.
"""

def generate_answer(query_engine, question, max_attempts_count = 3):
    attempts_count = 0
    while attempts_count < max_attempts_count:
        try:
            answer = query_engine.query(question).response
            break
        except:
            print("Failed generating answer.")
            attempts_count += 1
            if attempts_count < max_attempts_count:
                print("Retrying...")
            else: 
                print(f"There was an error producing answer for question:\n'{question}'.")
                return None
    return answer

def create_updated_dataset_knowledge(notes_llm, notes_llm_instructions, json_regex, notes_llm_prompt, max_attempts_count = 3):
    attempts_count = 0
    while attempts_count < max_attempts_count:
        try:
            res = notes_llm.complete(notes_llm_instructions + notes_llm_prompt)
            res_json = extract_json_part(json_regex, str(res))
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

def create_query_engine_tools(index_storage_context_dicts_paths, llm):
    tool_metadata_provider = {
        "additional_info_index.json": ToolMetadata(
            name="Additional information",
            description="Provides additional information about the dataset",
        ),
        "csv_files_index.json": ToolMetadata(
            name="CSV files",
            description="Provides actual dataset (all CSV files)",
        ),
        "reports_index.json": ToolMetadata(
            name="Data profiling reports",
            description="Provides reports generated from data profiling of CSV files",
        ),
    }
    
    query_engine_tools = [
        QueryEngineTool(
            query_engine=load_index(path).as_query_engine(llm=llm),
            metadata=tool_metadata_provider[Path(path).name]
        )
        for path in index_storage_context_dicts_paths]

    return query_engine_tools

def create_prompting_phase_llm(prompting_phase_instructions):
    return Ollama(
        model="deepseek-r1:8b", 
        request_timeout=420.0, 
        system_prompt=prompting_phase_instructions
    )

def create_notes_llm(notes_llm_instructions):
    return Ollama(
        model="deepseek-r1:8b", 
        request_timeout=420.0, 
        # For some reason the system prompt is not working when LLM.complete() is used. That is why 
        # I prepend instructions (system prompt) at the beginning of the prompt later when using Notes LLM.
        # system_prompt=notes_llm_instructions
    )

def create_query_engine(index_storage_context_dicts_paths, llm):
    query_engine_tools = create_query_engine_tools(index_storage_context_dicts_paths, llm)
    
    query_engine = SubQuestionQueryEngine.from_defaults(
        query_engine_tools=query_engine_tools,
        llm=llm,
        verbose=False
    )
    
    return query_engine

def create_initial_dataset_knowledge(prompting_phase_prompts, query_engine, notes_llm, notes_llm_instructions):    
    json_regex = re.compile(r'```json([\s\S]*?)```')
    dataset_knowledge = '{\n"tables": []\n}'
    for prompting_phase_prompt in prompting_phase_prompts:
        answer = generate_answer(query_engine, prompting_phase_prompt)
        if not answer:
            continue

        notes_llm_prompt = create_notes_llm_prompt(
            dataset_knowledge, prompting_phase_prompt, answer.strip())
        # notes llm prompt contains current dataset knowledge
        updated_dataset_knowledge = create_updated_dataset_knowledge(
            notes_llm, notes_llm_prompt, json_regex, notes_llm_instructions)
        if not updated_dataset_knowledge:
            continue

        dataset_knowledge = updated_dataset_knowledge

    return dataset_knowledge

def main(args):
    index_storage_context_dicts_paths = get_file_paths(Path(args.indices_folder_path))

    prompting_phase_instructions = read_file(args.prompting_phase_instructions_path)
    prompting_phase_llm = create_prompting_phase_llm(prompting_phase_instructions)

    notes_llm_instructions = read_file(args.notes_llm_instructions_path)
    notes_llm = create_notes_llm(notes_llm_instructions)

    query_engine = create_query_engine(index_storage_context_dicts_paths, prompting_phase_llm)

    prompting_phase_prompts = read_file(args.prompting_phase_prompts_path, load_as_json=True)
    initial_dataset_knowledge = create_initial_dataset_knowledge(
        prompting_phase_prompts, query_engine, notes_llm, notes_llm_instructions)

    with open(args.output_file_path, 'w') as output_file:
        json.dump(initial_dataset_knowledge, output_file)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
