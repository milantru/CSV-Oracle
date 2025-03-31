import argparse
import json
from shared_helpers import read_file, get_model, DatasetKnowledge, get_embedding_model, create_individual_query_engine_tools, create_sub_question_query_engine, get_chroma_db_client

parser = argparse.ArgumentParser(description="Script for generating an initial dataset knowledge representation.")
parser.add_argument("-c", "--collection_names", type=str, required=True, help="JSON string containing list of ChromaDb collection names (for retrieving indices).")
parser.add_argument("-p", "--prompting_phase_prompts_path", type=str, required=True, help="Path to the input file containing prompting phase prompts.")
parser.add_argument("-r", "--prompting_phase_instructions_path", type=str, required=True, help="Path to the input file containing prompting phase instructions.")
parser.add_argument("-o", "--output_file_path", type=str, required=True, help="Path to the file where the initial dataset knowledge representation should be stored. The new file will be created, or overwritten if already exists.")

def generate_answer(query_engine, question, max_attempts_count = 3):
    answer = ""
    if not question:
        print("Skipping empty question...")
        return None
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

def create_query_engine(collection_names, db, llm, embedding_model):
    query_engine_tools = create_individual_query_engine_tools(
        collection_names, db, llm, embedding_model)
    
    query_engine = create_sub_question_query_engine(query_engine_tools, llm)
    
    return query_engine

def try_answer_question(query_engine, question):
    answer = generate_answer(query_engine, question)
    return answer if answer else ""

def create_initial_dataset_knowledge(prompting_phase_prompts: DatasetKnowledge, query_engine):
    # prompting_phase_prompts is basically dataset knowledge we want to create but has questions in place of answers
    # so the goal is to answer the questions and replace the questions with its answers
    prompting_phase_prompts.description = try_answer_question(query_engine, prompting_phase_prompts.description)
    
    for table_knowledge in prompting_phase_prompts.table_knowledges:
        table_knowledge.description = try_answer_question(query_engine, table_knowledge.description)
        table_knowledge.row_entity_description = try_answer_question(query_engine, table_knowledge.row_entity_description)
        for column_knowledge in table_knowledge.column_knowledges:
            column_knowledge.description = try_answer_question(query_engine, column_knowledge.description)
            column_knowledge.missing_values_explanation = try_answer_question(query_engine, column_knowledge.missing_values_explanation)
        for correlation_explanation in table_knowledge.correlation_explanations:
            correlation_explanation.explanation = try_answer_question(query_engine, correlation_explanation.explanation)

    return prompting_phase_prompts

def main(args):
    llm = get_model(
        model = "llama3.3:latest", 
        system_prompt = read_file(args.prompting_phase_instructions_path)
    )

    query_engine = create_query_engine(
        collection_names = json.loads(args.collection_names), 
        db = get_chroma_db_client(), 
        llm = llm,
        embedding_model = get_embedding_model()
    )

    prompting_phase_prompts = DatasetKnowledge.from_dict(read_file(args.prompting_phase_prompts_path, load_as_json=True))
    initial_dataset_knowledge = create_initial_dataset_knowledge(prompting_phase_prompts, query_engine)

    with open(args.output_file_path, 'w') as output_file:
        json.dump(initial_dataset_knowledge.to_dict(), output_file)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
