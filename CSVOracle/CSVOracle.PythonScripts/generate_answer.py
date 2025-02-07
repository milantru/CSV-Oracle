import argparse
import json
import re
from pathlib import Path
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import ReActAgent, ReActChatFormatter
from llama_index.core.llms import ChatMessage, MessageRole
from shared_helpers import get_file_paths, read_file, load_index, create_notes_llm, create_notes_llm_prompt, create_updated_dataset_knowledge

parser = argparse.ArgumentParser(description="Script for chat managing (answering messages in a chat fashion).")
parser.add_argument("-i", "--indices_folder_path", type=str, required=True, help="Path to the input folder containing index files (or to be more precise, index storage context dictionary files).")
parser.add_argument("-d", "--dataset_knowledge_path", type=str, required=True, help="Path to the file containing dataset knowledge.")
parser.add_argument("-u", "--user_view_path", type=str, default=None, help="(Optional) Path to the file containing user view.")
parser.add_argument("-c", "--chat_history_path", type=str, default=None, help="(Optional) Path to the file containing chat history. If not provided, the new chat is started creating a new chat history.")
parser.add_argument("-m", "--message_path", type=str, required=True, help="Path to the file containing the new message sent by the user to the chat.")
parser.add_argument("-n", "--notes_llm_instructions_path", type=str, required=True, help="Path to the input file containing Notes LLM instructions prompt.")
parser.add_argument("-s", "--updated_chat_history_path", type=str, required=True, help="Path to the file where the updated chat history should be stored. The new file will be created, or overwritten if already exists.")
parser.add_argument("-t", "--updated_dataset_knowledge_path", type=str, required=True, help="Path to the file where the updated dataset knowledge should be stored. The new file will be created, or overwritten if already exists.")
parser.add_argument("-a", "--answer_path", type=str, required=True, help="Path to the file where the answer to the message should be stored. The new file will be created, or overwritten if already exists.")

def create_query_engine_tools(index_storage_context_dicts_paths, llm):
    tool_metadata_provider = {
        "additional_info_index.json": ToolMetadata(
            name="additional_dataset_information",
            description=(
                "Provides additional information about the dataset"
                "Use a detailed plain text question as input to the tool."
            ),
        ),
        "csv_files_index.json": ToolMetadata(
            name="CSV_files",
            description=(
                "Provides actual dataset (all CSV files)"
                "Use a detailed plain text question as input to the tool."
            ),
        ),
        "reports_index.json": ToolMetadata(
            name="data_profiling_reports",
            description=(
                "Provides reports generated from data profiling of CSV files"
                "Use a detailed plain text question as input to the tool."
            ),
        ),
    }
    
    query_engine_tools = [
        QueryEngineTool(
            query_engine=load_index(path).as_query_engine(llm=llm),
            metadata=tool_metadata_provider[Path(path).name]
        )
        for path in index_storage_context_dicts_paths]

    return query_engine_tools

def create_chat_llm():
    return Ollama(
        model="deepseek-r1:8b", 
        request_timeout=420.0
    )

def create_agent(index_storage_context_dicts_paths, llm, instructions=None, chat_history=None):
    query_engine_tools = create_query_engine_tools(index_storage_context_dicts_paths, llm)
    
    agent = ReActAgent.from_tools(
        tools=query_engine_tools, 
        llm=llm,
        chat_history=chat_history,
        context=instructions,
        # react_chat_formatter=ReActChatFormatter.from_defaults(
        #     observation_role=MessageRole.TOOL,
        #     context=instructions,
        # ),
        verbose=True
    )
    
    return agent

def generate_chat_llm_instructions(user_view = None):
    instructions = f'''\
INSTRUCTIONS:
- You are part of an application called CSV Oracle, designed to help software engineers understand their data.
- Your task is to act as an assistant, helping software engineers comprehend their dataset and assess its suitability for their projects.
- There is a thing called "the dataset knowledge". It refers to the known dataset information stored in JSON format.
- While chatting with the user:
    - There might occur a new dataset information which should be added to the dataset knowledge.
    - User might ask you to update the dataset knowledge explicitly (add, remove, or rewrite some information).
- You can interact with the dataset knowledge using tags `<instr>` and '</instr>'. Between these tags should be instructions on how to edit the dataset knowledge.
    - Example: `<instr>Add to the dataset knowledge: The column X represents the Y.</instr>`.
- It is expected that software engineer speaks English, so use English as a default language.
'''
    if user_view:
        instructions = instructions + f"- The user view of the dataset is: \"{user_view}\"."
    return instructions

def load_chat_history(chat_history_dicts_path):
    chat_history_dicts = read_file(chat_history_dicts_path, load_as_json=True)
    chat_history = [ChatMessage.model_validate(x) for x in chat_history_dicts]
    return chat_history

def save_chat_history(file_path, chat_history):
    chat_history_dicts = [x.model_dump() for x in chat_history]
    with open(file_path, 'w') as output_file:
        json.dump(chat_history_dicts, output_file)

def extract_instructions(text):
    # Regular expression to find all <instr>...</instr> blocks
    pattern = re.compile(r'<instr>(.*?)</instr>', re.DOTALL)
    
    instructions = pattern.findall(text)
    cleaned_text = pattern.sub('', text)
    
    return instructions, cleaned_text.strip()

def main(args):
    index_storage_context_dicts_paths = get_file_paths(Path(args.indices_folder_path))

    chat_llm = create_chat_llm()

    user_view = read_file(args.user_view_path)
    chat_llm_instructions = generate_chat_llm_instructions(user_view)
    
    chat_history = load_chat_history(args.chat_history_path) if args.chat_history_path else None
    
    agent = create_agent(index_storage_context_dicts_paths, chat_llm, chat_llm_instructions, chat_history)
    
    message = read_file(args.message_path)

    response = agent.chat(message)

    notes_llm_instructions, answer = extract_instructions(str(response))
    if len(notes_llm_instructions) > 0:
        dataset_knowledge = read_file(args.dataset_knowledge_path, load_as_json=True)
        notes_llm_system_instructions = read_file(args.notes_llm_instructions_path)
        notes_llm = create_notes_llm(notes_llm_system_instructions)

        for instruction in notes_llm_instructions:
            notes_llm_prompt = create_notes_llm_prompt(dataset_knowledge, instruction)
            dataset_knowledge = create_updated_dataset_knowledge(
                    notes_llm, notes_llm_system_instructions + notes_llm_prompt)
            
        with open(args.updated_dataset_knowledge_path, 'w') as output_file:
            json.dump(dataset_knowledge, output_file)

    save_chat_history(args.updated_chat_history_path, agent.chat_history)

    with open(args.answer_path, 'w') as f:
        f.write(answer)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
