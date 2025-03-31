import re
import json
import argparse
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.core.agent.react.formatter import ReActChatFormatter
from llama_index.core.llms import ChatMessage, MessageRole
from shared_helpers import read_file, get_model, DatasetKnowledge, get_embedding_model, create_individual_query_engine_tools, create_sub_question_query_engine, get_chroma_db_client
from concurrent.futures import ThreadPoolExecutor

parser = argparse.ArgumentParser(description="Script for chat managing (answering messages in a chat fashion).")
parser.add_argument("-c", "--collection_names", type=str, required=True, help="JSON string containing list of ChromaDb collection names (for retrieving indices).")
parser.add_argument("-d", "--dataset_knowledge_path", type=str, required=True, help="Path to the file containing dataset knowledge.")
parser.add_argument("-u", "--user_view_path", type=str, default=None, help="(Optional) Path to the file containing user view.")
parser.add_argument("-r", "--chat_history_path", type=str, default=None, help="(Optional) Path to the file containing chat history. If not provided, the new chat is started creating a new chat history.")
parser.add_argument("-m", "--message_path", type=str, required=True, help="Path to the file containing the new message sent by the user to the chat.")
parser.add_argument("-s", "--updated_chat_history_path", type=str, required=True, help="Path to the file where the updated chat history should be stored. The new file will be created, or overwritten if already exists.")
parser.add_argument("-t", "--updated_dataset_knowledge_path", type=str, required=True, help="Path to the file where the updated dataset knowledge should be stored. The new file will be created, or overwritten if already exists.")
# TODO Do we need answer_path?
parser.add_argument("-a", "--answer_path", type=str, required=True, help="Path to the file where the answer to the message should be stored. The new file will be created, or overwritten if already exists.")
parser.add_argument("-k", "--api_keys", type=json.loads, required=True, help="A dictionary as a JSON string containing api keys as values. Currently supported keys are GROQ_API_KEY")

# TODO probably does not have to be global, can be done using capturing
GLOBALS = {
    "dataset_knowledge": None
}

def create_sub_question_query_engine_tool(query_engine_tools, llm, return_direct=False):
    sub_question_query_engine = create_sub_question_query_engine(query_engine_tools, llm)

    sub_question_query_engine_tool = QueryEngineTool(
        query_engine=sub_question_query_engine,
        metadata=ToolMetadata(
            name="sub_question_query_engine",
            description="Useful for when you want to answer queries that require analyzing all of the dataset information sources",
            return_direct=return_direct
        )
    )

    return sub_question_query_engine_tool

def create_agent(llm, tools, instructions=None, chat_history=None):    
    agent = ReActAgent.from_tools(
        tools=tools, 
        llm=llm,
        chat_history=chat_history,
        # context=instructions,
        react_chat_formatter=ReActChatFormatter.from_defaults(
            observation_role=MessageRole.TOOL,
            context=instructions,
        ),
        verbose=False
    )
    
    return agent

def generate_chat_llm_instructions(user_view = None):
    instructions = f'''\
INSTRUCTIONS:
- You are part of an application called CSV Oracle, designed to help software engineers understand their data.
- Your task is to act as an assistant, helping software engineers comprehend their dataset and assess its suitability for their projects.
- There is a thing called "dataset knowledge". It refers to the known dataset information which already contains some information at the beginning of the converstation but can updated while chatting with the user using proper tools.
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

def extract_instructions(text):
    # Regular expression to find all <instr>...</instr> blocks
    pattern = re.compile(r'<instr>(.*?)</instr>', re.DOTALL)
    
    instructions = pattern.findall(text)
    cleaned_text = pattern.sub('', text)
    
    return instructions, cleaned_text.strip()

# DatasetKnowledge functions
def get_dataset_description() -> str:
    """Retrieves the description of the dataset from the dataset knowledge."""
    return GLOBALS["dataset_knowledge"].description

def update_dataset_description(new_description: str) -> None:
    """Updates the description of the dataset in the dataset knowledge.
    
    Args:
        new_description (str): The new description for the dataset.
    """
    GLOBALS["dataset_knowledge"].description = new_description

# TableKnowledge functions
def get_table_description(table_name: str) -> str:
    """Retrieves the description of a specified table from the dataset knowledge.
    
    Args:
        table_name (str): The name of the table.
    
    Returns:
        str: The table description or an error message if the table is not found.
    """
    for table_knowledge in GLOBALS["dataset_knowledge"].table_knowledges:
        if table_knowledge.name == table_name:
            return table_knowledge.description
    return f"Table with name {table_name} was not found."

def update_table_description(table_name: str, new_description: str) -> None:
    """Updates the description of a specified table in the dataset knowledge.
    
    Args:
        table_name (str): The name of the table.
        new_description (str): The new description for the table.
    """
    for table_knowledge in GLOBALS["dataset_knowledge"].table_knowledges:
        if table_knowledge.name == table_name:
            table_knowledge.description = new_description
            break

def get_table_row_entity_description(table_name: str) -> str:
    """Retrieves the row entity description of a specified table from the dataset knowledge.
    
    Args:
        table_name (str): The name of the table.
    
    Returns:
        str: The row entity description or an error message if the table is not found.
    """
    for table_knowledge in GLOBALS["dataset_knowledge"].table_knowledges:
        if table_knowledge.name == table_name:
            return table_knowledge.row_entity_description
    return f"Table with name {table_name} was not found."

def update_table_row_entity_description(table_name: str, new_description: str) -> None:
    """Updates the row entity description of a specified table in the dataset knowledge.
    
    Args:
        table_name (str): The name of the table.
        new_description (str): The new row entity description.
    """
    for table_knowledge in GLOBALS["dataset_knowledge"].table_knowledges:
        if table_knowledge.name == table_name:
            table_knowledge.row_entity_description = new_description
            break

# ColumnKnowledge functions
def find_column_knowledge(dataset_knowledge: DatasetKnowledge, table_name: str, column_name: str):
    for table_knowledge in dataset_knowledge.table_knowledges:
        if table_knowledge.name == table_name:
            for column_knowledge in table_knowledge.column_knowledges:
                if column_knowledge.name == column_name:
                    return column_knowledge
    return None

def get_column_description(table_name: str, column_name: str) -> str:
    """Retrieves the description of a specified column from the dataset knowledge.
    
    Args:
        table_name (str): The name of the table.
        column_name (str): The name of the column.
    
    Returns:
        str: The column description or an error message if the column is not found.
    """
    column_knowledge = find_column_knowledge(GLOBALS["dataset_knowledge"], table_name, column_name)
    return column_knowledge.description if column_knowledge else \
        f"Column {column_name} was not found in table {table_name}."

def update_column_description(table_name: str, column_name: str, new_description: str) -> None:
    """Updates the description of a specified column in the dataset knowledge.
    
    Args:
        table_name (str): The name of the table.
        column_name (str): The name of the column.
        new_description (str): The new description for the column.
    """
    column_knowledge = find_column_knowledge(GLOBALS["dataset_knowledge"], table_name, column_name)
    if column_knowledge:
        column_knowledge.description = new_description

def get_missing_values_explanation(table_name: str, column_name: str) -> str:
    """Retrieves the explanation for missing values in a specified column from the dataset knowledge.
    
    Args:
        table_name (str): The name of the table.
        column_name (str): The name of the column.
    
    Returns:
        str: The missing values explanation or an error message if the column is not found.
    """
    column_knowledge = find_column_knowledge(GLOBALS["dataset_knowledge"], table_name, column_name)
    return column_knowledge.missing_values_explanation if column_knowledge else \
        f"Column {column_name} was not found in table {table_name}."

def update_missing_values_explanation(table_name: str, column_name: str, new_missing_values_explanation: str) -> None:
    """Updates the explanation for missing values in a specified in from the dataset knowledge.
    
    Args:
        table_name (str): The name of the table.
        column_name (str): The name of the column.
        new_missing_values_explanation (str): The new explanation for missing values.
    """
    column_knowledge = find_column_knowledge(GLOBALS["dataset_knowledge"], table_name, column_name)
    if column_knowledge:
        column_knowledge.missing_values_explanation = new_missing_values_explanation

def get_correlation_explanation(table_name: str, column1_name: str, column2_name: str) -> str:
    """Retrieves the correlation explanation between two specified columns from the dataset knowledge.
    
    Args:
        table_name (str): The name of the table.
        column1_name (str): The name of the first column.
        column2_name (str): The name of the second column.
    
    Returns:
        str: The correlation explanation or an error message if a column is not found.
    """
    column1_knowledge = find_column_knowledge(GLOBALS["dataset_knowledge"], table_name, column1_name)
    if not column1_knowledge:
        return f"Column {column1_name} was not found in table {table_name}."
    for correlation_explanation in column1_knowledge.correlation_explanations:
        if correlation_explanation.column2_name == column2_name:
            return correlation_explanation.explanation
    return f"Column {column2_name} was not found in table {table_name}."

def update_correlation_explanation(table_name: str, column1_name: str, column2_name: str, new_explanation: str) -> None:
    """Updates the correlation explanation between two specified columns in the dataset knowledge.
    
    Args:
        table_name (str): The name of the table.
        column1_name (str): The name of the first column.
        column2_name (str): The name of the second column.
        new_explanation (str): The new correlation explanation.
    """
    column1_knowledge = find_column_knowledge(GLOBALS["dataset_knowledge"], table_name, column1_name)
    if not column1_knowledge:
        return
    for correlation_explanation in column1_knowledge.correlation_explanations:
        if correlation_explanation.column2_name == column2_name:
            correlation_explanation.explanation = new_explanation

def create_func_tools():
    func_tools = []
    
    func_tools.append(FunctionTool.from_defaults(fn=get_dataset_description))
    
    func_tools.append(FunctionTool.from_defaults(fn=update_dataset_description))

    func_tools.append(FunctionTool.from_defaults(fn=get_table_description))

    func_tools.append(FunctionTool.from_defaults(fn=update_table_description))

    func_tools.append(FunctionTool.from_defaults(fn=get_table_row_entity_description))

    func_tools.append(FunctionTool.from_defaults(fn=update_table_row_entity_description))
    
    func_tools.append(FunctionTool.from_defaults(fn=get_column_description))

    func_tools.append(FunctionTool.from_defaults(fn=update_column_description))

    func_tools.append(FunctionTool.from_defaults(fn=get_missing_values_explanation))

    func_tools.append(FunctionTool.from_defaults(fn=update_missing_values_explanation))

    func_tools.append(FunctionTool.from_defaults(fn=get_correlation_explanation))

    func_tools.append(FunctionTool.from_defaults(fn=update_correlation_explanation))
    
    return func_tools

def create_query_engine_tools(collection_names, db, chat_llm, embedding_model):
    # return_direct set to True should speed up answering (unfortunatelly for the price of answer quality)
    individual_query_engine_tools = create_individual_query_engine_tools(collection_names, db, chat_llm, embedding_model, return_direct=True)
    sub_question_query_engine_tool = create_sub_question_query_engine_tool(individual_query_engine_tools, chat_llm, return_direct=True)
    return individual_query_engine_tools + [sub_question_query_engine_tool]

def save_dataset_knowledge(output_file_path: str, dataset_knowledge: DatasetKnowledge):
    with open(output_file_path, 'w') as output_file:
        json.dump(dataset_knowledge.to_dict(), output_file)

def save_chat_history(output_file_path, chat_history):
    chat_history_dicts = [x.model_dump() for x in chat_history]
    with open(output_file_path, 'w') as output_file:
        json.dump(chat_history_dicts, output_file)

def main(args):
    # Load
    user_view = read_file(args.user_view_path) if args.user_view_path else None
    chat_llm_instructions = generate_chat_llm_instructions(user_view)
    
    GLOBALS["dataset_knowledge"] = DatasetKnowledge.from_dict(read_file(args.dataset_knowledge_path, load_as_json=True))

    chat_llm = get_model(model="llama3.3:latest")

    query_engine_tools = create_query_engine_tools(
        collection_names = args.collection_names,
        db = get_chroma_db_client(),
        chat_llm = chat_llm,
        embedding_model = get_embedding_model()
    )
    func_tools = create_func_tools()

    tools = query_engine_tools + func_tools
    
    chat_history = load_chat_history(args.chat_history_path) if args.chat_history_path else None
    agent = create_agent(chat_llm, tools, chat_llm_instructions, chat_history)
    
    message = read_file(args.message_path)

    # Generate answer (no need to persist it on the disk, the answer is present in the chat history which is persisted later)
    answer = agent.chat(message)

    # Write
    with ThreadPoolExecutor() as executor:
        future1 = executor.submit(save_dataset_knowledge, args.updated_dataset_knowledge_path, GLOBALS["dataset_knowledge"])
        future2 = executor.submit(save_chat_history, args.updated_chat_history_path, agent.chat_history)

        # Wait for writing results to complete
        future1.result()
        future2.result()

        # TODO Do we need this?
        # answer = str(answer)
        # with open(args.answer_path, 'w') as f:
        #     f.write(answer)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
