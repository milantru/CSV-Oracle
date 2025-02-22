import argparse
import json
import re
from pathlib import Path
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import ReActAgent, ReActChatFormatter
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.llms.groq import Groq
from shared_helpers import get_file_paths, read_file, load_index, get_model, DatasetKnowledge

parser = argparse.ArgumentParser(description="Script for chat managing (answering messages in a chat fashion).")
parser.add_argument("-i", "--indices_folder_path", type=str, required=True, help="Path to the input folder containing index files (or to be more precise, index storage context dictionary files).")
parser.add_argument("-d", "--dataset_knowledge_path", type=str, required=True, help="Path to the file containing dataset knowledge.")
parser.add_argument("-u", "--user_view_path", type=str, default=None, help="(Optional) Path to the file containing user view.")
parser.add_argument("-c", "--chat_history_path", type=str, default=None, help="(Optional) Path to the file containing chat history. If not provided, the new chat is started creating a new chat history.")
parser.add_argument("-m", "--message_path", type=str, required=True, help="Path to the file containing the new message sent by the user to the chat.")
parser.add_argument("-s", "--updated_chat_history_path", type=str, required=True, help="Path to the file where the updated chat history should be stored. The new file will be created, or overwritten if already exists.")
parser.add_argument("-t", "--updated_dataset_knowledge_path", type=str, required=True, help="Path to the file where the updated dataset knowledge should be stored. The new file will be created, or overwritten if already exists.")
parser.add_argument("-a", "--answer_path", type=str, required=True, help="Path to the file where the answer to the message should be stored. The new file will be created, or overwritten if already exists.")
parser.add_argument("-k", "--api_keys", type=json.loads, required=True, help="A dictionary as a JSON string containing api keys as values. Currently supported keys are GROQ_API_KEY")

def create_query_engine_tools(index_storage_context_dicts_paths, llm):
    tool_metadata_provider = {
        "additional_info_index.json": ToolMetadata(
            name="additional_dataset_information",
            description=(
                "Provides text with additional information about the dataset provided by the user."
                "Use a detailed plain text question as input to the tool."
            ),
        ),
        "csv_files_index.json": ToolMetadata(
            name="csv_files",
            description=(
                "Provides actual dataset (all CSV files)."
                "Useful for when you want to access raw data of the dataset."
                "Use a detailed plain text question as input to the tool."
            ),
        ),
        "reports_index.json": ToolMetadata(
            name="data_profiling_reports",
            description=(
                "Provides reports generated from data profiling of csv files."
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

def create_sub_question_query_engine_tool_from(query_engine_tools, llm):
    sub_question_query_engine = SubQuestionQueryEngine.from_defaults(
        query_engine_tools=query_engine_tools,
        llm=llm
    )

    sub_question_query_engine_tool = QueryEngineTool(
        query_engine=sub_question_query_engine,
        metadata=ToolMetadata(
            name="sub_question_query_engine",
            description="Useful for when you want to answer queries that require analyzing all of the dataset information sources",
        )
    )

    return sub_question_query_engine_tool

def create_agent(llm, tools, instructions=None, chat_history=None):    
    agent = ReActAgent.from_tools(
        tools=tools, 
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
    - The user might refer to the dataset knowledge as notes.
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

def create_func_tools(dataset_knowledge):
    func_tools = []
    
    # DatasetKnowledge functions
    def get_dataset_description() -> str:
        """Returns the description of the dataset."""
        return dataset_knowledge.description
    func_tools.append(FunctionTool.from_defaults(fn=get_dataset_description))
    
    def update_dataset_description(new_description: str) -> None:
        """Updates the description of the dataset.
        
        Args:
            new_description (str): The new description for the dataset.
        """
        dataset_knowledge.description = new_description
    func_tools.append(FunctionTool.from_defaults(fn=update_dataset_description))

    # TableKnowledge functions
    def get_table_description(table_name: str) -> str:
        """Retrieves the description of a specified table.
        
        Args:
            table_name (str): The name of the table.
        
        Returns:
            str: The table description or an error message if the table is not found.
        """
        for table_knowledge in dataset_knowledge.table_knowledges:
            if table_knowledge.name == table_name:
                return table_knowledge.description
        return f"Table with name {table_name} was not found."
    func_tools.append(FunctionTool.from_defaults(fn=get_table_description))

    def update_table_description(table_name: str, new_description: str) -> None:
        """Updates the description of a specified table.
        
        Args:
            table_name (str): The name of the table.
            new_description (str): The new description for the table.
        """
        for table_knowledge in dataset_knowledge.table_knowledges:
            if table_knowledge.name == table_name:
                table_knowledge.description = new_description
                break
    func_tools.append(FunctionTool.from_defaults(fn=update_table_description))

    def get_table_row_entity_description(table_name: str) -> str:
        """Retrieves the row entity description of a specified table.
        
        Args:
            table_name (str): The name of the table.
        
        Returns:
            str: The row entity description or an error message if the table is not found.
        """
        for table_knowledge in dataset_knowledge.table_knowledges:
            if table_knowledge.name == table_name:
                return table_knowledge.row_entity_description
        return f"Table with name {table_name} was not found."
    func_tools.append(FunctionTool.from_defaults(fn=get_table_row_entity_description))

    def update_table_row_entity_description(table_name: str, new_description: str) -> None:
        """Updates the row entity description of a specified table.
        
        Args:
            table_name (str): The name of the table.
            new_description (str): The new row entity description.
        """
        for table_knowledge in dataset_knowledge.table_knowledges:
            if table_knowledge.name == table_name:
                table_knowledge.row_entity_description = new_description
                break
    func_tools.append(FunctionTool.from_defaults(fn=update_table_row_entity_description))
    
    # ColumnKnowledge functions
    def find_column_knowledge(table_name, column_name):
        for table_knowledge in dataset_knowledge.table_knowledges:
            if table_knowledge.name == table_name:
                for column_knowledge in table_knowledge.column_knowledges:
                    if column_knowledge.name == column_name:
                        return column_knowledge
        return None
    
    def get_column_description(table_name: str, column_name: str) -> str:
        """Retrieves the description of a specified column.
        
        Args:
            table_name (str): The name of the table.
            column_name (str): The name of the column.
        
        Returns:
            str: The column description or an error message if the column is not found.
        """
        column_knowledge = find_column_knowledge(table_name, column_name)
        return column_knowledge.description if column_knowledge else \
            f"Column {column_name} was not found in table {table_name}."
    func_tools.append(FunctionTool.from_defaults(fn=get_column_description))

    def update_column_description(table_name: str, column_name: str, new_description: str) -> None:
        """Updates the description of a specified column.
        
        Args:
            table_name (str): The name of the table.
            column_name (str): The name of the column.
            new_description (str): The new description for the column.
        """
        column_knowledge = find_column_knowledge(table_name, column_name)
        if column_knowledge:
            column_knowledge.description = new_description
    func_tools.append(FunctionTool.from_defaults(fn=update_column_description))

    def get_missing_values_explanation(table_name: str, column_name: str) -> str:
        """Retrieves the explanation for missing values in a specified column.
        
        Args:
            table_name (str): The name of the table.
            column_name (str): The name of the column.
        
        Returns:
            str: The missing values explanation or an error message if the column is not found.
        """
        column_knowledge = find_column_knowledge(table_name, column_name)
        return column_knowledge.missing_values_explanation if column_knowledge else \
            f"Column {column_name} was not found in table {table_name}."
    func_tools.append(FunctionTool.from_defaults(fn=get_missing_values_explanation))

    def update_missing_values_explanation(table_name: str, column_name: str, new_missing_values_explanation: str) -> None:
        """Updates the explanation for missing values in a specified column.
        
        Args:
            table_name (str): The name of the table.
            column_name (str): The name of the column.
            new_missing_values_explanation (str): The new explanation for missing values.
        """
        column_knowledge = find_column_knowledge(table_name, column_name)
        if column_knowledge:
            column_knowledge.missing_values_explanation = new_missing_values_explanation
    func_tools.append(FunctionTool.from_defaults(fn=update_missing_values_explanation))

    def get_correlation_explanation(table_name: str, column1_name: str, column2_name: str) -> str:
        """Retrieves the correlation explanation between two specified columns.
        
        Args:
            table_name (str): The name of the table.
            column1_name (str): The name of the first column.
            column2_name (str): The name of the second column.
        
        Returns:
            str: The correlation explanation or an error message if a column is not found.
        """
        column1_knowledge = find_column_knowledge(table_name, column1_name)
        if not column1_knowledge:
            return f"Column {column1_name} was not found in table {table_name}."
        for correlation_explanation in column1_knowledge.correlation_explanations:
            if correlation_explanation.column2_name == column2_name:
                return correlation_explanation.explanation
        return f"Column {column2_name} was not found in table {table_name}."
    func_tools.append(FunctionTool.from_defaults(fn=get_correlation_explanation))

    def update_correlation_explanation(table_name: str, column1_name: str, column2_name: str, new_explanation: str) -> None:
        """Updates the correlation explanation between two specified columns.
        
        Args:
            table_name (str): The name of the table.
            column1_name (str): The name of the first column.
            column2_name (str): The name of the second column.
            new_explanation (str): The new correlation explanation.
        """
        column1_knowledge = find_column_knowledge(table_name, column1_name)
        if not column1_knowledge:
            return
        for correlation_explanation in column1_knowledge.correlation_explanations:
            if correlation_explanation.column2_name == column2_name:
                correlation_explanation.explanation = new_explanation
    func_tools.append(FunctionTool.from_defaults(fn=update_correlation_explanation))
    
    return func_tools

def main(args):
    # Load
    user_view = read_file(args.user_view_path) if args.user_view_path else None
    chat_llm_instructions = generate_chat_llm_instructions(user_view)
    
    dataset_knowledge = DatasetKnowledge.from_dict(read_file(args.dataset_knowledge_path, load_as_json=True))

    index_storage_context_dicts_paths = get_file_paths(Path(args.indices_folder_path))
    chat_llm = get_model(model="llama-3.3-70b-versatile", api_key=args.api_keys["GROQ_API_KEY"])
    # query_engine_llm = create_chat_llm()

    individual_query_engine_tools = create_query_engine_tools(index_storage_context_dicts_paths, chat_llm)
    sub_question_query_engine_tool = create_sub_question_query_engine_tool_from(individual_query_engine_tools, chat_llm)
    func_tools = create_func_tools(dataset_knowledge)
    tools = individual_query_engine_tools + [sub_question_query_engine_tool] + func_tools
    
    chat_history = load_chat_history(args.chat_history_path) if args.chat_history_path else None
    agent = create_agent(chat_llm, tools, chat_llm_instructions, chat_history)
    
    message = read_file(args.message_path)

    # Generate answer
    response = agent.chat(message)

    # Write
    answer = str(response)
    with open(args.updated_dataset_knowledge_path, 'w') as output_file:
            json.dump(dataset_knowledge.to_dict(), output_file)

    save_chat_history(args.updated_chat_history_path, agent.chat_history)

    with open(args.answer_path, 'w') as f:
        f.write(answer)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
