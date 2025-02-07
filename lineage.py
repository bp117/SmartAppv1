import pandas as pd
import json
import requests
import gcp_utils
from sqlglot import parse_one, exp

def call_gemini(prompt):
    api_endpoint = "..."  # Define the endpoint URL for Gemini API
    token = gcp_utils.get_creds().token  # Fetches authentication token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ],
                "role": "user"
            }
        ]
    }
    response = requests.post(api_endpoint, headers=headers, data=json.dumps(data), verify=False)
    return response

def read_sql_files(file_paths):
    """Reads and combines SQL text from multiple files."""
    sql_text = ""
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            sql_text += f"-- SQL from {file_path}\n" + file.read() + "\n\n"
    return sql_text

def preprocess_sql(sql_text):
    """Preprocess SQL to extract metadata and simplify structure."""
    parsed = parse_one(sql_text)
    tables = [table.name for table in parsed.find_all(exp.Table)]
    columns = [col.alias_or_name for col in parsed.find_all(exp.Column)]
    return {"tables": tables, "columns": columns}

def get_column_lineage(sql_text, target_table, target_column):
    """Sends SQL content and lineage extraction request to Gemini."""
    prompt = f"""
    Below is the SQL content extracted from multiple files:
    {sql_text}

    Your task is to analyze the lineage of the column `{target_column}` in the table `{target_table}`. Follow these steps carefully:

    1. **Identify the Target Column**: Locate the exact column `{target_column}` in the table `{target_table}`. If the column or table is not found in the SQL content, output "COLUMN NOT FOUND IN THE SQL PROCEDURE."

    2. **Trace the Column's Derivation**:
       - Analyze how `{target_column}` is populated. This may involve direct assignments, transformations, joins, subqueries, or derived columns.
       - Account for all intermediate steps, including:
         - Volatile/temporary tables created during the procedure.
         - Aliases used for tables or columns.
         - Indirect column derivations (e.g., columns derived from other columns).
         - Nested subqueries or Common Table Expressions (CTEs).

    3. **Map Source Tables and Columns**:
       - Identify all source tables and columns that contribute to the value of `{target_column}`.
       - Include the database/schema name if available.
       - For each source column, describe the mapping logic (e.g., direct assignment, transformation, aggregation, etc.).

    4. **Handle Edge Cases**:
       - If `{target_column}` is derived from a volatile/temporary table, trace back to the original source tables and columns.
       - If `{target_column}` is populated conditionally (e.g., via `CASE` statements), include the conditions in the mapping logic.
       - If `{target_column}` is derived indirectly (e.g., through intermediate calculations), include all intermediate steps.

    5. **Output Format**:
       Provide the lineage information in CSV format with the following columns:
       - `target_table`: The table containing the target column.
       - `target_column`: The target column being analyzed.
       - `source_db`: The database/schema of the source table (if applicable).
       - `source_table`: The source table contributing to the target column.
       - `source_column`: The source column contributing to the target column.
       - `mapping_logic`: A clear description of how the source column maps to the target column.

    6. **Additional Notes**:
       - Ignore comments in the SQL code.
       - Ensure 100% accuracy in mapping logic. If unsure about any part of the lineage, output "PARTIAL LINEAGE" and describe the ambiguity.

    Provide the final output in CSV format.
    """
    responses = call_gemini(prompt)
    return responses

def extract_csv_from_response(resp):
    """Extracts CSV formatted content from the response."""
    if resp.find(".csv") != -1:
        i1 = resp.find(".csv")
        i2 = i1 + resp[i1:].find("\n")
        resp1 = resp[i1:i2]
    return resp1

def one_iter():
    sql_text = read_sql_files(sql_files_sequence)
    preprocessed_data = preprocess_sql(sql_text)
    print("Preprocessed Data:", preprocessed_data)

    responses = get_column_lineage(sql_text, TARGET_TABLE, TARGET_COLUMN).json()
    lineage_text = responses["candidates"][0]["content"]["parts"][0]["text"]
    extracted_csv_text = extract_csv_from_response(lineage_text)
    print(extracted_csv_text)

    lineage_lines = extracted_csv_text.strip().split("\n")
    lineage_records = [line.split(",") for line in lineage_lines]
    df_lineage = pd.DataFrame(
        lineage_records,
        columns=["target_table", "target_column", "source_db", "source_table", "source_column", "mapping_logic"]
    )
    output_csv_path = "multi_stored_proc_lineage.csv"
    df_lineage.to_csv(output_csv_path, index=False)
    print("\nExtracted Multi-Stored Procedure Lineage:")
    print(df_lineage)
    print(f"\nLineage saved to: {output_csv_path}")
    return df_lineage

# Define the SQL files to process
sql_files_sequence = [
    "./GUARANTOR_NM/GUARANTOR_NM/SP_CNI_FACLTY_TO_CC.txt",
    "./GUARANTOR_NM/GUARANTOR_NM/SP_CNI_GUARANTOR_LVT.txt"
]
TARGET_TABLE = "CNI_FACLTY_TO_CC"
TARGET_COLUMN = "GUARANTOR_NM"

df1 = one_iter()
