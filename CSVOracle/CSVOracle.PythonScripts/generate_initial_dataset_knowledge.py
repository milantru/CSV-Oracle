import argparse
import json
from pathlib import Path
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.llms.ollama import Ollama
from llama_index.core.query_engine import SubQuestionQueryEngine
from shared_helpers import get_file_paths, read_file, load_index, get_model, DatasetKnowledge

parser = argparse.ArgumentParser(description="Script for generating an initial dataset knowledge representation.")
parser.add_argument("-i", "--indices_folder_path", type=str, required=True, help="Path to the input folder containing index files (or to be more precise, index storage context dictionary files).")
parser.add_argument("-p", "--prompting_phase_prompts_path", type=str, required=True, help="Path to the input file containing prompting phase prompts.")
parser.add_argument("-r", "--prompting_phase_instructions_path", type=str, required=True, help="Path to the input file containing prompting phase instructions.")
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

def create_query_engine(index_storage_context_dicts_paths, llm):
    query_engine_tools = create_query_engine_tools(index_storage_context_dicts_paths, llm)
    
    query_engine = SubQuestionQueryEngine.from_defaults(
        query_engine_tools=query_engine_tools,
        llm=llm,
        verbose=False
    )
    
    return query_engine

def try_answer_question(query_engine, question):
    answer = generate_answer(query_engine, question)
    return answer if answer else ""

def create_initial_dataset_knowledge(prompting_phase_prompts, query_engine):    
    # prompting_phase_prompts is basically dataset knowledge we want to create but has questions in place of answers
    # so the goal is to answer the questions and replace the questions with its answers
    prompting_phase_prompts.description = try_answer_question(query_engine, prompting_phase_prompts.description)
    
    for table_knowledge in prompting_phase_prompts.table_knowledges:
        table_knowledge.description = try_answer_question(query_engine, table_knowledge.description)
        table_knowledge.row_entity_description = try_answer_question(query_engine, table_knowledge.row_entity_description)
        for column_knowledge in table_knowledge.column_knowledges:
            column_knowledge.description = try_answer_question(query_engine, column_knowledge.description)
            column_knowledge.missing_values_explanation = try_answer_question(query_engine, column_knowledge.missing_values_explanation)
            for correlation_explanation in column_knowledge.correlation_explanations:
                correlation_explanation.explanation = try_answer_question(query_engine, correlation_explanation.explanation)

    return prompting_phase_prompts

def main(args):
    index_storage_context_dicts_paths = get_file_paths(Path(args.indices_folder_path))

    prompting_phase_instructions = read_file(args.prompting_phase_instructions_path)
    prompting_phase_llm = get_model(model="llama3.2:latest", system_prompt=prompting_phase_instructions)

    query_engine = create_query_engine(index_storage_context_dicts_paths, prompting_phase_llm)

    prompting_phase_prompts = DatasetKnowledge.from_dict(read_file(args.prompting_phase_prompts_path, load_as_json=True))
    initial_dataset_knowledge = create_initial_dataset_knowledge(prompting_phase_prompts, query_engine)

    with open(args.output_file_path, 'w') as output_file:
        json.dump(initial_dataset_knowledge.to_dict(), output_file)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
