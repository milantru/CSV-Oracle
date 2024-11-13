import argparse
import pandas as pd
from ydata_profiling import ProfileReport
import json
from pathlib import Path

parser = argparse.ArgumentParser(description="Script to generate a data profiling report and prompts for system prompting phase.")
parser.add_argument("-p", "--path_to_datasets", type=str, required=True, help="Path to the dataset folder.")
parser.add_argument("-s", "--separator", type=str, default=",", help="Separator used in the dataset.")
parser.add_argument("-e", "--encoding", type=str, default="utf-8", help="Encoding used in the dataset.")
parser.add_argument("-g", "--generate_html", type=bool, default=False, help="Flag for enabling HTML report generation.")
parser.add_argument("-a", "--additional_info", type=str, default="", help="Additional information about the dataset.")
parser.add_argument("-u", "--user_view", type=str, default="", help="User view of the dataset.")

def to_percentage(num):
    return round(num * 100, 2)
    
def create_sample_data(report, n=3, sep=","):
    head, tail = report["sample"]
    # tail is not checked because it is expected that 
    # if there is no head, there wont be neither tail 
    if len(head["data"]) == 0:
        return [], [], []
    column_names = sep.join(head["data"][0].keys())

    head_rows = [sep.join([str(value) for value in row.values()]) for row in head["data"][:n]]
    tail_rows = [sep.join([str(value) for value in row.values()]) for row in tail["data"][-n:]]

    all_rows = [column_names] + head_rows + ["..."] + tail_rows
    sample_data = "\n".join(all_rows)

    return sample_data

def process_column_data(column_data):
    # TODO What if more types?
    processed_column_data = {}

    # Generic (also Unsupported)
    if "type" in column_data: processed_column_data["Deduced type"] = column_data["type"]
    if "n_distinct" in column_data: processed_column_data["Distinct values count"] = column_data["n_distinct"]
    if "p_distinct" in column_data: processed_column_data["Distinct values count in %"] = to_percentage(column_data["p_distinct"])
    if "is_unique" in column_data: processed_column_data["Has only unique values"] = column_data["is_unique"]
    if "count" in column_data: processed_column_data["Values count (not nulls)"] = column_data["count"]
    if "n_missing" in column_data: processed_column_data["Missing values count"] = column_data["n_missing"]
    if "p_missing" in column_data: processed_column_data["Missing values count in %"] = to_percentage(column_data["p_missing"])

    # Numeric
    if "n_negative" in column_data: processed_column_data["Negative values count"] = column_data["n_negative"]
    if "p_negative" in column_data: processed_column_data["Negative values count in %"] = to_percentage(column_data["p_negative"])
    if "n_zeros" in column_data: processed_column_data["Zeros count"] = column_data["n_zeros"]
    if "p_zeros" in column_data: processed_column_data["Zeros count in %"] = to_percentage(column_data["p_zeros"])
    if "mean" in column_data: processed_column_data["Mean"] = column_data["mean"]
    if "std" in column_data: processed_column_data["Standard deviation"] = column_data["std"]
    if "mad" in column_data: processed_column_data["Median absolute deviation"] = column_data["mad"]
    if "variance" in column_data: processed_column_data["Variance"] = column_data["variance"]
    if "min" in column_data: processed_column_data["Minimum"] = column_data["min"]
    if "max" in column_data: processed_column_data["Maximum"] = column_data["max"]
    if "kurtosis" in column_data: processed_column_data["Kurtosis"] = column_data["kurtosis"]
    if "skewness" in column_data: processed_column_data["Skewness"] = column_data["skewness"]
    if "sum" in column_data: processed_column_data["Sum"] = column_data["sum"]
    
    # Text
    if "min_length" in column_data: processed_column_data["Min length"] = column_data["min_length"]
    if "max_length" in column_data: processed_column_data["Max length"] = column_data["max_length"]
    if "mean_length" in column_data: processed_column_data["Mean length"] = column_data["mean_length"]
    if "median_length" in column_data: processed_column_data["Median length"] = column_data["median_length"]
        
    # Categorical
    # Seems no categorical data is needed
    return processed_column_data

def add_columns_info_to_knowledge(dataset_knowledge, report):
    # First get info like missing values count, minimums, maximums, means, stds...
    processed_columns_data = {}
    for column_name, column_data in report["variables"].items():
        processed_column_data = process_column_data(column_data)
        processed_columns_data[column_name] = processed_column_data

    # Then for each column, get all columns that correlate with it.
    corr_threshold = 0.5
    # This if is here because for some reason sometimes there are no correlations. 
    # Probably insufficient data.
    if "auto" in report["correlations"]:
        cols_correlations = report["correlations"]["auto"]
        for i in range(len(cols_correlations)):
            col_i_correlations = cols_correlations[i]
            cols_correlated_with_col_i = []
            col_i_name = None
            for j, (col_j_name, corr_value) in enumerate(col_i_correlations.items()):
                if i == j:
                    col_i_name = col_j_name
                    continue
                if corr_value > corr_threshold:
                    cols_correlated_with_col_i.append(f"{col_j_name} (correlation value: {corr_value})")
            processed_columns_data[col_i_name]["Is correlated with columns"] = cols_correlated_with_col_i
    
    # Finally, update knowledge
    dataset_knowledge["Columns"] = processed_columns_data


def add_general_table_info_to_knowledge(dataset_knowledge, report):
    table_data = report["table"]
    
    dataset_knowledge["Row count"] = table_data["n"]
    dataset_knowledge["Column count"] = table_data["n_var"]
    dataset_knowledge["Missing cells count"] = table_data["n_cells_missing"]
    dataset_knowledge["Missing cells count in %"] = to_percentage(table_data["p_cells_missing"])

def create_dataset_knowledge(report):
    dataset_knowledge = {} # We will gradually add new knowledge about the dataset (new properties)
    
    add_general_table_info_to_knowledge(dataset_knowledge, report)
    add_columns_info_to_knowledge(dataset_knowledge, report)
    
    return dataset_knowledge

def create_instructions_prompt(csv_files_paths):
    def get_string(csv_files_names):
        csv_files_count = len(csv_files_names)
        if csv_files_count == 1:
            return f"1 table: {csv_files_names[0]}"
        else:
            tmp = ", ".join(csv_files_names)
            return f"{csv_files_count} tables: {tmp}"
    csv_files_names = [csv_file_path.name for csv_file_path in csv_files_paths]
    return f'''\
INSTRUCTIONS:
- You function as a tool for software engineers to answer questions about the dataset.
- First you will be given information about the dataset. Information like sample data and possibly schema, additional information about the dataset, user view, or output from data profiling.
- Then you will be prompted with questions about the dataset and you will answer them, aiming to extract as much information as possible.
- Your answers should be concise and to the point, containing only the answer to the question. So no other text, like for example "Feel free to ask me if you have more questions...".
- The dataset consists of {get_string(csv_files_names)}.
- The language of the dataset may differ from that of the user, who is expected to speak English. Because of that, you will answer questions about the dataset in English by default.

If you understand, please respond with "OK".\
'''

def create_data_prompt(csv_file_name, schema, sample_data, additional_info, user_view, data_profiling_output):
    prompt_with_input = f"Information about {csv_file_name}:\n"

    if schema: prompt_with_input += f'''Schema:\n"""\n{schema}\n"""\n\n'''
    prompt_with_input += f'''Sample data:\n"""\n{sample_data}\n"""\n\n'''
    if additional_info: prompt_with_input += f'''Additional information about the dataset:\n"""\n{additional_info}\n"""\n\n'''    
    if user_view: prompt_with_input += f'''User view:\n"""\n{user_view}\n"""\n\n'''
    if data_profiling_output: prompt_with_input += f'''Output from data profiling:\n"""\n{data_profiling_output}\n"""\n\n'''
    prompt_with_input += 'If you understand this input, just type "OK".'
    
    return prompt_with_input 

def add_column_prompts(prompts, csv_file_name, columns_knowledge):
    for col_name, col_info in columns_knowledge.items():
        column_prompt = f'Provide a brief description of the column {col_name} from table {csv_file_name}. What does it describe or represent? Answer only with the column description, no other text (tags are allowed).'
        prompts.append(column_prompt)

        # "Missing values count" is expected to always be in col_info, but we check its existience anyway 
        # because of defensive programming. And we do so in case of other properties as well.
        if ("Missing values count" in col_info and col_info["Missing values count"] > 0) \
        and ("Missing values count in %" in col_info and col_info["Missing values count in %"] > 0):
            column_prompt_missing_values = f'The column {col_name} from table {csv_file_name} has {col_info["Missing values count"]} missing values ({col_info["Missing values count in %"]} %). Provide an explanation why the values are missing. Answer only with the explanation, no other text (tags are allowed).'
            prompts.append(column_prompt_missing_values)
        
        if "Is correlated with columns" in col_info and len(col_info["Is correlated with columns"]) > 0:
            for correlated_col_name in col_info["Is correlated with columns"]:
                # correlated_col_name includes, apart from the col name, the corr value
                column_prompt_corr = f'Provide an explanation for why the column {col_name} from table {csv_file_name} is correlated with the column {correlated_col_name}. Answer only with the explanation, no other text (tags are allowed).'
                prompts.append(column_prompt_corr)

        # TODO (schema) for each column, if schema provided; chcelo by to schemu...
        # column_prompt_schema = 'Why does this constraint exist? Explain the reasoning behind the given constraint or rule in the schema.'
        # prompts.append(column_prompt_schema)

def create_data_profiling_report(args, csv_file_path):
    df = pd.read_csv(csv_file_path, sep=args.separator, encoding=args.encoding)

    type_schema = None # {"Survived": "categorical", "Embarked": "categorical"} # TODO (schema) Schema?
    profile = ProfileReport(df, title="CSV Oracle profiling report using ydata profiling", type_schema=type_schema)
    if args.generate_html:
        csv_filename = csv_file_path.stem
        profile.to_file(rf"reports\report_for_{csv_filename}.html")

    json_string = profile.to_json()
    report = json.loads(json_string)
    
    return report

def main(args):
    datasets_folder_path = Path(args.path_to_datasets)
    csv_files_paths = list(datasets_folder_path.glob("*.csv"))

    prompts = [create_instructions_prompt(csv_files_paths)]

    datasets_columns_knowledge = []
    for csv_file_path in csv_files_paths:
        report = create_data_profiling_report(args, csv_file_path)

        dataset_knowledge = create_dataset_knowledge(report)
        datasets_columns_knowledge.append(dataset_knowledge["Columns"])
        sample_data = create_sample_data(report, sep=args.separator)

        data_prompt = create_data_prompt(
            csv_file_name=csv_file_path.name,
            schema=None, # TODO (schema) try this also with schema
            sample_data=sample_data,
            additional_info=args.additional_info,
            user_view=args.user_view,
            data_profiling_output=dataset_knowledge
        )
        prompts.append(data_prompt)
    
    # Questions start
    tmp = " " if len(csv_files_paths) == 1 else " (as all tables together, prompts about each table separately will come later) "
    prompts.append(f"Summarize what the dataset{tmp}represents and explain what context or domain the data comes from. Be concise.")

    for i in range(len(csv_files_paths)):
        csv_file_name = csv_files_paths[i].name
        prompts.append(f"Summarize what the table {csv_file_name} represents and explain what context or domain the data comes from. Be concise.")
        prompts.append(f"What kind of entity or entities does the table row of {csv_file_name} represent? Make the answer concise.")
        dataset_columns_knowledge = datasets_columns_knowledge[i]
        add_column_prompts(prompts, csv_file_name, dataset_columns_knowledge)

    last_prompt = 'Just write "Hello! How can I help you with this dataset?"'
    if args.user_view:
        last_prompt = f'User view for the dataset was provided. User view:\n"""\n{args.user_view}\n"""\n\nIf you can answer the user need coming from the user view, write the answer as if you were writing it to the user (provide only answer, no questions, e.g. "Would you like assistance with some specific task?"). Otherwise just write "Hello! How can I help you with this dataset?".'
    prompts.append(last_prompt)

    # TODO Remove writing prompts to file
    with open("GENERATED_SYSTEM_PROMPTS.md", "w", encoding="utf-8") as file:
        file.write("```\n" + "\n```\n\n```\n".join(prompts) + "\n```\n")

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
