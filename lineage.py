import json
import requests
import gcp_utils

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

def build_dag(sql_text):
    """Sends SQL content and DAG construction request to Gemini."""
    prompt = f"""
    Below is the SQL content extracted from multiple files:
    {sql_text}

    Your task is to analyze the SQL code and construct a Directed Acyclic Graph (DAG) that represents the dependencies between tables and columns. Follow these steps carefully:

    1. **Identify Tables and Columns**:
       - Extract all table names and column names from the SQL code.
       - Include both permanent and temporary/volatile tables.
       - Account for aliases used for tables and columns.

    2. **Trace Dependencies**:
       - For each table and column, identify its dependencies on other tables and columns.
       - Include:
         - Direct references (e.g., `SELECT col1 FROM table1`).
         - Indirect references (e.g., columns derived through transformations or calculations).
         - Joins and subqueries.
         - Volatile/temporary tables and their relationships with permanent tables.
         - Aliases and their mappings to actual table/column names.

    3. **Handle Edge Cases**:
       - If a column is populated conditionally (e.g., via `CASE` statements), include the conditions as part of the dependency.
       - If a column is derived indirectly (e.g., through intermediate calculations), trace back to the original source columns.
       - If a table is created dynamically (e.g., `CREATE TABLE AS SELECT`), include the source tables and columns used in the `SELECT` statement.

    4. **Construct the DAG**:
       - Represent the dependencies as a DAG where:
         - Nodes represent tables and columns.
         - Edges represent dependencies between nodes.
       - For example:
         - An edge from `table1.col1` to `table2.col2` indicates that `col2` depends on `col1`.
         - An edge from `temp_table.colA` to `final_table.colB` indicates that `colB` is derived from `colA`.

    5. **Output Format**:
       Provide the DAG in JSON format with the following structure:
       ```json
       {{
           "nodes": [
               {{"id": "table1.col1", "type": "column"}},
               {{"id": "table2.col2", "type": "column"}},
               {{"id": "temp_table", "type": "table"}}
           ],
           "edges": [
               {{"source": "table1.col1", "target": "table2.col2", "relationship": "direct"}},
               {{"source": "temp_table.colA", "target": "final_table.colB", "relationship": "indirect"}}
           ]
       }}
       ```
       - Each node should have an `id` (e.g., `table1.col1`) and a `type` (`table` or `column`).
       - Each edge should have a `source`, `target`, and `relationship` (`direct`, `indirect`, or `conditional`).

    6. **Additional Notes**:
       - Ignore comments in the SQL code.
       - Ensure 100% accuracy in tracing dependencies. If unsure about any part of the DAG, output "PARTIAL DAG" and describe the ambiguity.

    Provide the final output in JSON format.
    """
    response = call_gemini(prompt).json()
    return response["candidates"][0]["content"]["parts"][0]["text"]

# Define the SQL files to process
sql_files_sequence = [
    "./GUARANTOR_NM/GUARANTOR_NM/SP_CNI_FACLTY_TO_CC.txt",
    "./GUARANTOR_NM/GUARANTOR_NM/SP_CNI_GUARANTOR_LVT.txt"
]

sql_text = read_sql_files(sql_files_sequence)
dag_json = build_dag(sql_text)

# Save the DAG to a file
with open("dag_output.json", "w") as file:
    file.write(dag_json)

print("\nDAG saved to dag_output.json")
