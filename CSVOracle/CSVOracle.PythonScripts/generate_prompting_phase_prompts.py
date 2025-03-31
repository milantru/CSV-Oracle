import argparse
import json
from pathlib import Path
from shared_helpers import DatasetKnowledge, TableKnowledge, ColumnKnowledge, CorrelationExplanation, Row

parser = argparse.ArgumentParser(description="Script for generating prompting phase question prompts for the LLM.")
parser.add_argument("-i", "--input_reports_folder_path", type=str, required=True, help="Path to the folder containing reports generated from the csv files of the dataset.")
parser.add_argument("-o", "--output_file_path", type=str, required=True, help="Path to the file where the question prompts should be written. It is a json following DatasetKnowledge class structure. The new file will be created, or overwritten if already exists.")

def to_percentage(num):
    return round(num * 100, 2)

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

    # DateTime
    # Comments like Numerical, Text, etc. are for guidance only, 
    # for example DateTime also contains "min" and "max", as the Numerical does, 
    # but the code is not written here for these properties to avoid code duplicity
    return processed_column_data

def add_columns_info(dataset_info_from_report, report):
    # First get info like missing values count, minimums, maximums, means, stds...
    processed_columns_data = {}
    for column_name, column_data in report["variables"].items():
        processed_column_data = process_column_data(column_data)
        processed_columns_data[column_name] = processed_column_data

    # Then for each column, get all columns that correlate with it.
    corr_threshold = 0.5
    # It seems that if there is insufficient ammount of data the correlations are not calculated and therefore missing,
    # that is why this if is here.
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
                    cols_correlated_with_col_i.append([col_j_name, round(corr_value, 2)])
            processed_columns_data[col_i_name]["Is correlated with columns"] = cols_correlated_with_col_i
    
    # Finally, update knowledge
    dataset_info_from_report["Columns"] = processed_columns_data

def get_sample_rows(report):
    def to_row(row_object):
        row = Row()
        row.values = list(row_object.values())
        return row

    sample_objects = report["sample"]
    head_rows, tail_rows = [], []
    for sample_object in sample_objects:
        if sample_object["id"] == "head":
            row_objects = sample_object["data"]
            head_rows = [to_row(row_object) for row_object in row_objects]
        elif sample_object["id"] == "tail":
            row_objects = sample_object["data"]
            tail_rows = [to_row(row_object) for row_object in row_objects]

    return head_rows, tail_rows

def add_general_table_info(dataset_info_from_report, report):
    table_data = report["table"]
    
    dataset_info_from_report["Row count"] = table_data["n"]
    dataset_info_from_report["Column count"] = table_data["n_var"]
    dataset_info_from_report["Missing cells count"] = table_data["n_cells_missing"]
    dataset_info_from_report["Missing cells count in %"] = to_percentage(table_data["p_cells_missing"])

    head_rows, tail_rows = get_sample_rows(report)
    dataset_info_from_report["Sample head"] = head_rows
    dataset_info_from_report["Sample tail"] = tail_rows

def create_dataset_info_from_report(report):
    dataset_info_from_report = {} # We will gradually add new info about the dataset (new properties)
    
    add_general_table_info(dataset_info_from_report, report)
    add_columns_info(dataset_info_from_report, report)
    
    return dataset_info_from_report

def add_column_prompts(table_knowledge: TableKnowledge, csv_file_name: str, column_info_from_report: dict):
    for col_name, col_info in column_info_from_report.items():
        # Create and add column knowledge
        column_knowledge = ColumnKnowledge()
        
        column_knowledge.name = col_name
        column_knowledge.description = f'Provide a brief description of the column {col_name} from table {csv_file_name}. What does it describe or represent? Answer only with the column description, no other text.'

        # "Missing values count" is expected to always be in col_info, but we check its existience anyway 
        # because of defensive programming. And we do so in case of other properties as well.
        if ("Missing values count" in col_info and col_info["Missing values count"] > 0) \
        and ("Missing values count in %" in col_info and col_info["Missing values count in %"] > 0):
            column_knowledge.missing_values_explanation = f'The column {col_name} from table {csv_file_name} has {col_info["Missing values count"]} missing values ({col_info["Missing values count in %"]} %). Provide an explanation why the values are missing. Answer only with the explanation, no other text.'
        
        table_knowledge.column_knowledges.append(column_knowledge)

        # Create and add correlation explanation
        if "Is correlated with columns" in col_info and len(col_info["Is correlated with columns"]) > 0:
            processed_pairs = {} # Keeps track of already processed column pairs
            for correlated_col_name, corr_value in col_info["Is correlated with columns"]:
                col1_name, col2_name = sorted([col_name, correlated_col_name])
                if col1_name in processed_pairs and col2_name in processed_pairs[col1_name]:
                    continue
                if col1_name not in processed_pairs:
                    processed_pairs[col1_name] = {}
                processed_pairs[col1_name][col2_name] = True

                correlation_explanation = CorrelationExplanation()
                correlation_explanation.column1_name = col1_name
                correlation_explanation.column2_name = col2_name
                correlation_explanation.correlation_value = corr_value
                correlation_explanation.explanation = f'Provide an explanation for why the columns {col1_name} and {col2_name} from table {csv_file_name} are correlated (correlation value: {corr_value}). Answer only with the explanation, no other text.'
                
                table_knowledge.correlation_explanations.append(correlation_explanation)

        # TODO (schema) for each column, if schema provided; chcelo by to schemu...
        # column_prompt_schema = 'Why does this constraint exist? Explain the reasoning behind the given constraint or rule in the schema.'
        # prompts.append(column_prompt_schema)

def main(args):
    reports_files_paths = list(Path(args.input_reports_folder_path).glob("*.json"))
    csv_files_names = [report_file_path.stem.removesuffix("_report") for report_file_path in reports_files_paths]

    dataset_info_from_reports = []
    for report_file_path in reports_files_paths:
        with open(report_file_path, 'r') as file:
            report = json.load(file)

        dataset_info_from_report = create_dataset_info_from_report(report)
        dataset_info_from_reports.append(dataset_info_from_report)

    # Questions start
    # We start creating dataset knowledge (the one the user will interact with), we will now mostly fill it with questions
    # that will be used in prompting phase to get more info. Maybe a bit of a hacky solution but works nicely - this way 
    # the structure of the knowledge is secured.
    dataset_knowledge = DatasetKnowledge()

    tmp = " " if len(csv_files_names) == 1 else " (as all tables together, prompts about each table separately will come later) "
    dataset_knowledge.description = f"Summarize what the dataset{tmp}represents and explain what context or domain the data comes from. Be concise."

    for i in range(len(csv_files_names)):
        table_knowledge = TableKnowledge()
        csv_file_name = csv_files_names[i]
        dataset_info_from_report = dataset_info_from_reports[i]

        table_knowledge.name = csv_file_name
        table_knowledge.description = f"Summarize what the table {csv_file_name} represents and explain what context or domain the data comes from. Be concise."
        table_knowledge.row_entity_description = f"What kind of entity or entities does the table row of {csv_file_name} represent? Make the answer concise."
        table_knowledge.sample_head = dataset_info_from_report["Sample head"]
        table_knowledge.sample_tail = dataset_info_from_report["Sample tail"]
        
        column_info_from_report = dataset_info_from_report["Columns"]
        add_column_prompts(table_knowledge, csv_file_name, column_info_from_report)
        
        dataset_knowledge.table_knowledges.append(table_knowledge)
    
    with open(args.output_file_path, "w") as file:
        json.dump(dataset_knowledge.to_dict(), file)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
