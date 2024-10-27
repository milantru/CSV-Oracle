import argparse
import os
import pandas as pd
from ydata_profiling import ProfileReport
import json


parser = argparse.ArgumentParser(description="Script to generate a data profiling report and prompts.")
# TODO check args (path to dataset default? encoding ok? addit. info and user view default to "")
parser.add_argument("-p", "--path_to_dataset", type=str, default=r"datasets\navigator2022.csv", help="Path to the dataset file")
parser.add_argument("-s", "--separator", type=str, default=";", help="Separator used in the dataset")
parser.add_argument("-e", "--encoding", type=str, default="ISO-8859-1", help="Encoding used in the dataset")
parser.add_argument("-g", "--generate_html", type=bool, default=False, help="Flag for enabling HTML report generation")
parser.add_argument("-a", "--additional_info", type=str,
    default='''\
Geographical overview of thermal waste treatment facilities

Yearly updated geographical navigator: The geographic navigator presents overall annual information about facilities for the incineration and co-incineration of waste, which are obtained from summary operating records. These are the following: identification number (IČ), name of the facility, address of the operator, address of the facility, putting into operation, types of waste incinerated, nominal capacity, amount of waste incinerated in tonnes per year, number and brief description of incineration lines, enumeration of equipment for reducing emissions, annual emissions of all pollutants reported.

The Czech Hydrometeorological Institute processes and continuously updates the database of equipment for thermal treatment of waste in cooperation with ČIŽP. Pursuant to Article 55 of Directive 2010/75/EU, which regulates access to information and public participation, we are making available a list of all thermal waste treatment facilities.\
''', 
    help="Path to the dataset file")
parser.add_argument("-u", "--user_view", type=str,
    default="I want to use this dataset to create a software which will visualise on the map where are the facilities for the incineration located and which type of waste can be incinerated there.", 
    help="Path to the dataset file")


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
    cols_correlations = report["correlations"]["auto"] # TODO Is auto OK?
    for i in range(len(cols_correlations)):
        col_i_correlations = cols_correlations[i]
        cols_correlated_with_col_i = []
        col_i_name = None
        for j, (col_j_name, corr_value) in enumerate(col_i_correlations.items()):
            if i == j:
                col_i_name = col_j_name
                continue
            if corr_value > corr_threshold:
                cols_correlated_with_col_i.append(col_j_name)
        processed_columns_data[col_i_name]["Is correlated with columns"] = cols_correlated_with_col_i
    
    # Finally, update knowledge
    dataset_knowledge["Columns"] = processed_columns_data


def add_general_table_info_to_knowledge(dataset_knowledge, report):
    table_data = report["table"]
    
    dataset_knowledge["Row count"] = table_data["n"]
    dataset_knowledge["Column count"] = table_data["n_var"]
    dataset_knowledge["Missing cells count"] = table_data["n_cells_missing"]
    dataset_knowledge["Missing cells count in %"] = to_percentage(table_data["p_cells_missing"])

def create_dataset_knowledge(args, report):
    dataset_knowledge = {} # We will gradually add new knowledge about the dataset (new properties)
    
    add_general_table_info_to_knowledge(dataset_knowledge, report)
    add_columns_info_to_knowledge(dataset_knowledge, report)
    
    return dataset_knowledge

def create_instructions_prompt():
    return '''\
Instructions:
- You are an assistant for the software engineers.
- Your job is to help the software engineers to understand the data they provide and assess its suitability for their project needs.
- In the next message you will receive an input in this format:
Dataset schema:
"""
{Dataset schema}
"""

Sample of the dataset:
"""
{Sample of the dataset}
"""

Additional info about the dataset:
"""
{Additional info about the dataset}
"""

User view for this dataset:
"""
{User view for this dataset}
"""

Output from the data profiling of the dataset:
"""
{Output from the data profiling of the dataset}
"""

- Some parts of the input are optional and might be left out.
- After receiving the mentioned input, you may analyze it. Afterwards you will be prompted by premade system prompts (not user prompts) to answer questions about the dataset. Your answers will be processed and displayed to the user.
- You will be notified when the premade system prompts end and the user prompts will begin by message "PREMADE SYSTEM PROMPTS HAS ENDED, USER PROMPTS START NOW". After that you will be speaking to the user and you will answer user's questions regarding the dataset and the user's view (if provided).
- It is expected that the dataset does not belong to the user and thus the language of the dataset may differ from the language of the user.
- It is expected that the user speaks English. Because of that you will answer question about the dataset in English.
- If you understand your job, just type OK.\
'''

def create_data_prompt(schema, sample_data, additional_info, user_view, data_profiling_output):
    prompt_with_input = ""

    if schema: prompt_with_input += f'''Dataset schema:\n"""\n{schema}\n"""\n\n'''
    prompt_with_input += f'''Sample of the dataset:\n"""\n{sample_data}\n"""\n\n'''
    if additional_info: prompt_with_input += f'''Additional info about the dataset:\n"""\n{additional_info}\n"""\n\n'''    
    if user_view: prompt_with_input += f'''User view for this dataset:\n"""\n{user_view}\n"""\n\n'''
    if data_profiling_output: prompt_with_input += f'''Output from the data profiling of the dataset:\n"""\n{data_profiling_output}\n"""\n\n'''
    prompt_with_input += "If you understand this input, just type OK."
    
    return prompt_with_input 

def create_prompts(args, sample_data, dataset_knowledge):
    prompts = [
        create_instructions_prompt(),
        create_data_prompt(
            schema=None, # TODO (schema) try this also with schema
            sample_data=sample_data,
            additional_info=args.additional_info,
            user_view=args.user_view,
            data_profiling_output=dataset_knowledge
        ),
        "Summarize what the dataset represents and explain what context or domain the data comes from. Be concise.",
        "What kind of entity or entities does the table row represent? Make the answer concise.",
    ]

    for col_name, col_info in dataset_knowledge["Columns"].items():
        column_prompt = f'Provide a brief description of the column {col_name}. What does it describe or represent? Answer only with the column description, no other text.'
        prompts.append(column_prompt)

        # "Missing values count" is expected to always be in col_info, but we check its existience anyway 
        # because of defensive programming. And we do so in case of other properties as well.
        if "Missing values count" in col_info and col_info["Missing values count"] > 0:
            column_prompt_missing_values = f'Provide a likely explanation as to why the values are missing in column {col_name}. Answer only with the explanation, no other text. If you have no explanation, just write "I have no explanation".'
            prompts.append(column_prompt_missing_values)
        
        if "Is correlated with columns" in col_info and len(col_info["Is correlated with columns"]) > 0:
            for correlated_col_name in col_info["Is correlated with columns"]:
                column_prompt_corr = f'Provide a likely explanation for why the column {col_name} is correlated with column {correlated_col_name}. Answer only with the explanation, no other text. If you have no explanation, just write "I have no explanation".'
                prompts.append(column_prompt_corr)

        # TODO (schema) for each column, if schema provided; chcelo by to schemu...
        # column_prompt_schema = 'Why does this constraint exist? Explain the reasoning behind the given constraint or rule in the schema.'
        # prompts.append(column_prompt_schema)

    if args.user_view:
        user_view_prompt = '''If user view for the dataset is provided and you can deduce the user's question as well as the answer from the this view, write the answer as if you were writing it to the user. Otherwise write "Hello! How can I help you with this dataset?".''' 
        prompts.append(user_view_prompt)

    end_prompt = 'PREMADE SYSTEM PROMPTS HAS ENDED, USER PROMPTS START NOW\n\nIf you understand, just write OK.'
    prompts.append(end_prompt)

    return prompts

def create_data_profiling_report(args):
    df = pd.read_csv(args.path_to_dataset, sep=args.separator, encoding=args.encoding)

    type_schema = None # {"Survived": "categorical", "Embarked": "categorical"} # TODO (schema) Schema?
    profile = ProfileReport(df, title="CSV Oracle profiling report using ydata profiling", type_schema=type_schema)
    if args.generate_html:
        profile.to_file(r"reports\report.html")

    json_string = profile.to_json()
    report = json.loads(json_string)
    
    return report

def main(args):
    report = create_data_profiling_report(args)

    dataset_knowledge = create_dataset_knowledge(args, report)
    sample_data = create_sample_data(report, sep=args.separator)

    prompts = create_prompts(args, sample_data, dataset_knowledge)

    # TODO Remove writing prompts to file
    with open("PROMPTS.md", "w", encoding="utf-8") as file:
        file.write("```\n" + "\n```\n\n```\n".join(prompts) + "\n```\n")

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
