import json
import argparse
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.core.agent.react.formatter import ReActChatFormatter
from llama_index.core.llms import ChatMessage, MessageRole
from shared_helpers import (
    read_file,
    get_model,
    get_embedding_model,
    create_individual_query_engine_tools,
    create_sub_question_query_engine,
    get_chroma_db_client,
    DatasetKnowledge
)
from concurrent.futures import ThreadPoolExecutor

parser = argparse.ArgumentParser(description="Script for chat managing (answering messages in a chat fashion).")
parser.add_argument(
    "-c", "--collection_names", type=str, required=True, 
    help="JSON string containing list of ChromaDb collection names (for retrieving indices)."
)
parser.add_argument(
    "-d", "--dataset_knowledge_path", type=str, required=True, 
    help="Path to the file containing dataset knowledge."
)
parser.add_argument("-u", "--user_view_path", type=str, default=None, help="(Optional) Path to the file containing user view.")
parser.add_argument(
    "-r", "--chat_history_path", type=str, default=None, 
    help=(
        "(Optional) Path to the file containing chat history. "
        "If not provided, the new chat is started creating a new chat history."
    )
)
parser.add_argument(
    "-m", "--message_path", type=str, required=True, 
    help="Path to the file containing the new message sent by the user to the chat."
)
parser.add_argument(
    "-s", "--updated_chat_history_path", type=str, required=True, 
    help=(
        "Path to the file where the updated chat history should be stored. "
        "The new file will be created, or overwritten if already exists."
    )
)
parser.add_argument(
    "-t", "--updated_dataset_knowledge_path", type=str, required=True, 
    help=(
        "Path to the file where the updated dataset knowledge should be stored. "
        "The new file will be created, or overwritten if already exists."
    )
)
# if model requires api key, following argument can be used to retrieve the key and one can pass it to get_model later in code
parser.add_argument(
    "-k", "--api_keys", type=json.loads, required=True, 
    help="A dictionary as a JSON string which can contain api keys as values."
)

GLOBALS = {
    "dataset_knowledge": None
}

def create_sub_question_query_engine_tool(query_engine_tools, llm, schema_provided, return_direct=False):
    sub_question_query_engine = create_sub_question_query_engine(query_engine_tools, llm)

    desc = None
    if schema_provided:
        desc = "Useful for when you want to answer queries that require analyzing either csv files, data profiling reports, dataset knowledge, or csvw schema."
    else:
        desc = "Useful for when you want to answer queries that require analyzing either csv files, data profiling reports, or dataset knowledge."

    sub_question_query_engine_tool = QueryEngineTool(
        query_engine=sub_question_query_engine,
        metadata=ToolMetadata(
            name="sub_question_query_engine",
            description=desc,
            return_direct=return_direct
        )
    )

    return sub_question_query_engine_tool

def create_agent(llm, tools, instructions=None, chat_history=None):    
    agent = ReActAgent.from_tools(
        tools=tools, 
        llm=llm,
        chat_history=chat_history,
        react_chat_formatter=ReActChatFormatter.from_defaults(
            observation_role=MessageRole.TOOL,
            context=instructions
        ),
        verbose=False
    )
    
    return agent

def get_shared_columns(dataset_knowledge):
    tmp = {}
    for table_knowledge in dataset_knowledge.table_knowledges:
        for column_knowledge in table_knowledge.column_knowledges:
            if column_knowledge.name not in tmp:
                tmp[column_knowledge.name] = []
            if table_knowledge.name in tmp[column_knowledge.name]:
                # I expect this should never happen, it would mean the table
                # has at least two columns with the same name. This if was added
                # because of defense programming, to make sure the same table name would not be
                # in the list multiple times.
                continue
            tmp[column_knowledge.name].append(table_knowledge.name)
    
    # Filter to keep only columns that appear in more than one table
    shared_columns = {column: list(tables) for column, tables in tmp.items() if len(tables) > 1}
    return shared_columns

def generate_chat_llm_instructions(dataset_knowledge: DatasetKnowledge, user_view = None):    
    shared_columns_section = ""
    if len(dataset_knowledge.table_knowledges) > 1:
        shared_columns = get_shared_columns(dataset_knowledge)
        if len(shared_columns.items()) > 0:
            shared_columns_str = "\n".join(
                f"    - '{col}': {", ".join(tables)}" for col, tables in shared_columns.items()
            )
            shared_columns_section = f"""
Handling Duplicate Column Names Across Files:
- The following columns appear in more than one CSV file:
{shared_columns_str}
- When referencing these columns in your responses, always qualify them with the name of the file they belong to (e.g. id from orders, where id is column name and orders is table name).
- If a user refers to a column that exists in more than one file without specifying which file they mean, and the context is not clearly disambiguated, ask for clarification before proceeding.
- Do not assume which file the column belongs to unless it is explicitly stated or strongly implied by the context.
"""

    instructions = f'''\
INSTRUCTIONS:
- You are part of an application called CSV Oracle, designed to help software engineers and data analysts understand and work with their datasets.
- Your primary role is to assist users in exploring, analyzing, and making decisions based on their datasets.
{shared_columns_section}
About Dataset Knowledge:
- Dataset Knowledge refers to a structured summary or collection of insights extracted from the uploaded dataset.
- This knowledge is available at the beginning of the conversation and can be updated dynamically throughout the session.
- Users may refer to it as "notes," "dataset info," or similar terms.
- The dataset knowledge may not be complete at the beginning of the conversation. For example, if you use a tool to retrieve dataset knowledge and it returns an empty result, this simply means no information has been added yet. You can help build it over time.

During Conversation:
- Be proactive in identifying new insights from user queries or interactions that can be added to the dataset knowledge.
- If a user explicitly requests to update the dataset knowledge (add, remove, or rewrite content), use the appropriate tools to apply those changes.
- When updating dataset knowledge (e.g. descriptions), always retrieve the current value first, modify it accordingly, and then update it. The update functions overwrite existing values.
- Keep the dataset knowledge accurate and up to date. If there is any ambiguity or uncertainty, ask the user for clarification before applying updates.
- Treat the dataset knowledge as a shared, evolving document that both you and the user can contribute to.
- You can output the names of the files, but not the full paths.
- Please do not output table name like "table.csv", use just "table" without ".csv".
- ALWAYS try to answer the original question!
- Be concise!
'''
    if user_view:
        user_view_section = f'''
User View (Background Context Only):
- The user has provided the following background information about their perspective on the dataset:
"{user_view}"

IMPORTANT: This user view is for context only. Use it to better understand the user's perspective, but do not act on it unless the user explicitly refers to it in their current message. Always treat the user's latest message as the primary instruction.
'''
        instructions += user_view_section
    
    return instructions

def load_chat_history(chat_history_dicts_path):
    chat_history_dicts = read_file(chat_history_dicts_path, load_as_json=True)
    chat_history = [ChatMessage.model_validate(x) for x in chat_history_dicts]
    return chat_history

# DatasetKnowledge functions
def update_dataset_description(new_description: str) -> str:
    """Updates the description of the dataset in the dataset knowledge.

    IMPORTANT:
    - This function will overwrite the current description.
    - To modify or append to the existing description, first retrieve current dataset description using `dataset_knowledge` tool.
      Then update that value as needed, and pass the complete, modified version into this function.

    Args:
        new_description (str): The full, updated description for the dataset.

    Returns:
        str: A confirmation message indicating the description was successfully updated.
    """
    GLOBALS["dataset_knowledge"].description = new_description
    return "Dataset description updated successfully."

# TableKnowledge functions
def find_table_knowledge(dataset_knowledge: DatasetKnowledge, table_name: str):
    for table_knowledge in dataset_knowledge.table_knowledges:
        if table_knowledge.name == table_name:
            return table_knowledge
    return None

def update_table_description(table_name: str, new_description: str) -> str:
    """Updates the description of a specified table in the dataset knowledge.

    IMPORTANT:
    - This function will overwrite the current table description.
    - To modify or append to the existing description, first retrieve current table description using `dataset_knowledge` tool.
      Then update that value as needed, and pass the complete, modified version into this function.

    Args:
        table_name (str): The name of the table.
        new_description (str): The full, updated description for the table.

    Returns:
        str: A message indicating success or failure.
    """
    table_knowledge = find_table_knowledge(GLOBALS["dataset_knowledge"], table_name)
    if table_knowledge:
        table_knowledge.description = new_description
        return f"Description for table '{table_name}' updated successfully."
    else:
        return f"Error: Table with name '{table_name}' not found. Invalid table name provided."

def get_table_row_entity_description(table_name: str) -> str:
    """Retrieves the row entity description of a specified table from the dataset knowledge.
    
    Args:
        table_name (str): The name of the table.
    
    Returns:
        str: The row entity description or an error message if the table is not found.
    """
    table_knowledge = find_table_knowledge(GLOBALS["dataset_knowledge"], table_name)
    if table_knowledge:
        return table_knowledge.row_entity_description
    else:
        return f"Error: Table with name '{table_name}' not found. Invalid table name provided."

def update_table_row_entity_description(table_name: str, new_description: str) -> str:
    """Updates the row entity description of a specified table in the dataset knowledge.

    IMPORTANT:
    - This function will overwrite the current row entity description.
    - To modify or append to the existing description, first retrieve table row entity description using `dataset_knowledge` tool.
      Then update that value as needed, and pass the complete, modified version into this function.

    Args:
        table_name (str): The name of the table.
        new_description (str): The full, updated row entity description.

    Returns:
        str: A message indicating success or failure.
    """
    table_knowledge = find_table_knowledge(GLOBALS["dataset_knowledge"], table_name)
    if table_knowledge:
        table_knowledge.row_entity_description = new_description
        return f"Row entity description for table '{table_name}' updated successfully."
    else:
        return f"Error: Table with name '{table_name}' not found. Invalid table name provided."

# ColumnKnowledge functions
def find_column_knowledge(dataset_knowledge: DatasetKnowledge, table_name: str, column_name: str):
    table_knowledge = find_table_knowledge(dataset_knowledge, table_name)
    if not table_knowledge:
        return None
    
    for column_knowledge in table_knowledge.column_knowledges:
        if column_knowledge.name == column_name:
            return column_knowledge
    
    return None

def get_err_msg(column_name, table_name):
    err_msg = f"Error: Column '{column_name}' not found in table '{table_name}'."
    table_knowledge = find_table_knowledge(GLOBALS["dataset_knowledge"], table_name)
    if table_knowledge:
        return err_msg + " Invalid column name provided."
    else:
        return err_msg + " Invalid table name provided." # Column name could be also wrong, should find out in next iteration if so 

def update_column_description(table_name: str, column_name: str, new_description: str) -> str:
    """Updates the description of a specified column in the dataset knowledge.

    IMPORTANT:
    - This function will overwrite the current column description.
    - To modify or append to the existing description, first retrieve column description using `dataset_knowledge` tool.
      Then update that value as needed, and pass the complete, modified version into this function.

    Args:
        table_name (str): The name of the table.
        column_name (str): The name of the column.
        new_description (str): The full, updated description for the column.

    Returns:
        str: A message indicating success or failure.
    """
    column_knowledge = find_column_knowledge(GLOBALS["dataset_knowledge"], table_name, column_name)
    if column_knowledge:
        column_knowledge.description = new_description
        return f"Description of column '{column_name}' in table '{table_name}' updated successfully."
    else:
        return get_err_msg(column_name, table_name)

def update_missing_values_explanation(table_name: str, column_name: str, new_missing_values_explanation: str) -> str:
    """Updates the explanation for missing values in a specified column in the dataset knowledge.

    IMPORTANT:
    - This function will overwrite the current explanation.
    - To modify or append to the existing explanation, first retrieve missing values explanation using `dataset_knowledge` tool.
      Then update that value as needed, and pass the complete, modified version into this function.

    Args:
        table_name (str): The name of the table.
        column_name (str): The name of the column.
        new_missing_values_explanation (str): The full, updated explanation for missing values.

    Returns:
        str: A message indicating success or failure.
    """
    column_knowledge = find_column_knowledge(GLOBALS["dataset_knowledge"], table_name, column_name)
    if column_knowledge:
        column_knowledge.missing_values_explanation = new_missing_values_explanation
        return f"Explanation for missing values in column '{column_name}' in table '{table_name}' updated successfully."
    else:
        return get_err_msg(column_name, table_name)

# CorrelationExplanation functions
def try_find_correlation_explanation(dataset_knowledge: DatasetKnowledge, table_name: str, column1_name: str, column2_name: str):
    table_knowledge = find_table_knowledge(dataset_knowledge, table_name)
    
    err_msg = f"Error: Correlation explanation for columns '{column1_name}' and '{column2_name}' not found in table '{table_name}.'"
    if not table_knowledge:
        return (err_msg + " Invalid table name provided.", False) # Colum names could be also wrong, should find out in next iteration if so
    
    for correlation_explanation in table_knowledge.correlation_explanations:
        if (correlation_explanation.column1_name == column1_name and correlation_explanation.column2_name == column2_name) \
            or correlation_explanation.column1_name == column2_name and correlation_explanation.column2_name == column1_name:
            return (correlation_explanation, True)

    # Explanation was not returned, now we try to find out why 
    column1_knowledge = find_column_knowledge(dataset_knowledge, table_name, column1_name)
    column2_knowledge = find_column_knowledge(dataset_knowledge, table_name, column2_name)
    if column1_knowledge is None and column2_knowledge is None:
        return (err_msg + " Both 'column1_name' and 'column2_name' are invalid.", False)
    elif column1_knowledge is not None and column2_knowledge is None:
        return (err_msg + " Column 'column2_name' is invalid.", False)
    elif column1_knowledge is None and column2_knowledge is not None:
        return (err_msg + " Column 'column1_name' is invalid.", False)
    else:
        return (err_msg, False) # This should never happen, but for the sake of defensive programming, this code is present

def update_correlation_explanation(table_name: str, column1_name: str, column2_name: str, new_explanation: str) -> str:
    """Updates the correlation explanation between two specified columns in the dataset knowledge.

    IMPORTANT:
    - This function will overwrite the current correlation explanation between the two columns.
    - To modify or append to the existing explanation, first retrieve correlation explanation using `dataset_knowledge` tool.
      Then update that value as needed, and pass the complete, modified version into this function.

    Args:
        table_name (str): The name of the table.
        column1_name (str): The name of the first column.
        column2_name (str): The name of the second column.
        new_explanation (str): The full, updated correlation explanation.

    Returns:
        str: A message indicating success or failure.
    """
    correlation_explanation_or_err_msg, is_found = try_find_correlation_explanation(
        GLOBALS["dataset_knowledge"], table_name, column1_name, column2_name)
    
    if is_found:
        correlation_explanation_or_err_msg.explanation = new_explanation
        return f"Explanation for correlation of columns '{column1_name}' and '{column2_name}' in table '{table_name}' updated successfully."
    else:
        return correlation_explanation_or_err_msg

def create_func_tools():
    func_tools = []
    
    func_tools.append(FunctionTool.from_defaults(fn=update_dataset_description))

    func_tools.append(FunctionTool.from_defaults(fn=update_table_description))

    func_tools.append(FunctionTool.from_defaults(fn=update_table_row_entity_description))
    
    func_tools.append(FunctionTool.from_defaults(fn=update_column_description))

    func_tools.append(FunctionTool.from_defaults(fn=update_missing_values_explanation))

    func_tools.append(FunctionTool.from_defaults(fn=update_correlation_explanation))
    
    return func_tools

def create_query_engine_tools(collection_names, db, chat_llm, embedding_model):
    individual_query_engine_tools = create_individual_query_engine_tools(collection_names, db, chat_llm, embedding_model, return_direct=False, dataset_knowledge=GLOBALS["dataset_knowledge"])
    sub_question_query_engine_tool = create_sub_question_query_engine_tool(individual_query_engine_tools, chat_llm, len(collection_names) == 3, return_direct=False)
    return individual_query_engine_tools + [sub_question_query_engine_tool]

def save_dataset_knowledge(output_file_path: str, dataset_knowledge: DatasetKnowledge):
    with open(output_file_path, 'w') as output_file:
        json.dump(dataset_knowledge.to_dict(), output_file)

def save_chat_history(output_file_path, chat_history):
    chat_history_dicts = [x.model_dump() for x in chat_history]
    with open(output_file_path, 'w') as output_file:
        json.dump(chat_history_dicts, output_file)

def main(args: argparse.Namespace):
    """
    Executes a chat-based interaction for analyzing CSV datasets (generates answer for the message specified via args).

    Loads dataset knowledge, user message, and optional chat history and user view. Initializes the LLM agent 
    with tools for querying data and updating knowledge. Processes the user message, updates the 
    chat history and possibly also dataset knowledge, and writes them to specified output files.

    Args:
        args (argparse.Namespace): Command-line arguments.
    """
    # Load
    user_view = read_file(args.user_view_path) if args.user_view_path else None
    GLOBALS["dataset_knowledge"] = DatasetKnowledge.from_dict(read_file(args.dataset_knowledge_path, load_as_json=True))
    chat_llm_instructions = generate_chat_llm_instructions(GLOBALS["dataset_knowledge"], user_view)

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

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
