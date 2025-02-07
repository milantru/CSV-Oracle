import argparse
import json
import re
from pathlib import Path
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.llms.ollama import Ollama
from llama_index.core.query_engine import SubQuestionQueryEngine
from shared_helpers import get_file_paths, read_file, load_index, create_notes_llm, create_updated_dataset_knowledge, create_notes_llm_prompt

parser = argparse.ArgumentParser(description="Script for generating an initial dataset knowledge representation.")
parser.add_argument("-i", "--indices_folder_path", type=str, required=True, help="Path to the input folder containing index files (or to be more precise, index storage context dictionary files).")
parser.add_argument("-p", "--prompting_phase_prompts_path", type=str, required=True, help="Path to the input file containing prompting phase prompts.")
parser.add_argument("-r", "--prompting_phase_instructions_path", type=str, required=True, help="Path to the input file containing prompting phase instructions.")
parser.add_argument("-n", "--notes_llm_instructions_path", type=str, required=True, help="Path to the input file containing Notes LLM instructions prompt.")
parser.add_argument("-o", "--output_file_path", type=str, required=True, help="Path to the file where the initial dataset knowledge representation should be stored. The new file will be created, or overwritten if already exists.")


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

def create_query_engine(index_storage_context_dicts_paths, llm):
    query_engine_tools = create_query_engine_tools(index_storage_context_dicts_paths, llm)
    
    query_engine = SubQuestionQueryEngine.from_defaults(
        query_engine_tools=query_engine_tools,
        llm=llm,
        verbose=False
    )
    
    return query_engine

def create_instruction_for_notes_llm(question, answer):
    return f"""\
The answer for the question "{question}" was:
"{answer}"

Please, based on the provided answer, add the newly gained information to the CURRENT DATASET KNOWLEDGE.
"""

def create_initial_dataset_knowledge(prompting_phase_prompts, query_engine, notes_llm, notes_llm_instructions):    
    json_regex = re.compile(r'```json([\s\S]*?)```') # perf improvement so we dont have to compile every iteration
    dataset_knowledge = '{\n"tables": []\n}'
    for prompting_phase_prompt in prompting_phase_prompts:
        answer = generate_answer(query_engine, prompting_phase_prompt)
        if not answer:
            continue

        instruction = create_instruction_for_notes_llm(prompting_phase_prompt, answer.strip())
        # notes llm prompt contains current dataset knowledge
        notes_llm_prompt = create_notes_llm_prompt(dataset_knowledge, instruction)
        updated_dataset_knowledge = create_updated_dataset_knowledge(
            notes_llm, notes_llm_instructions + notes_llm_prompt, json_regex=json_regex)
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
