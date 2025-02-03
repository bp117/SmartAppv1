import openai
import pandas as pd

# Define OpenAI API Key (Replace with your actual API key)
OPENAI_API_KEY = "your-api-key"

# List of SQL files containing stored procedures
sql_file_paths = [
    "path/to/sql_file1.sql",
    "path/to/sql_file2.sql",
    "path/to/sql_file3.sql"
]

# Define the target table and column for lineage extraction
TARGET_TABLE = "CNI_FACLTY_TO_CC"  # Modify as needed
TARGET_COLUMN = "GUARANTOR_NM"  # Modify as needed

# Function to read all SQL files together
def read_sql_files(file_paths):
    """Reads and combines SQL text from multiple files."""
    sql_text = ""
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            sql_text += f"-- SQL from {file_path} --\n" + file.read() + "\n\n"
    return sql_text

# Function to call GPT-4 for lineage extraction
def get_column_lineage(sql_text, target_table, target_column):
    """Sends SQL content and lineage extraction request to GPT-4."""
    prompt = f"""
    You are an expert in SQL lineage analysis. Your task is to analyze multiple SQL stored procedures and views
    across several files. Identify the complete column-level lineage for the column '{target_column}' in the table '{target_table}'.

    - If one stored procedure calls another, trace the data flow across them.
    - Identify all transformations, joins, and dependencies between tables.
    - Resolve temporary tables and trace lineage back to the original source.
    - The input SQL contains multiple procedures, analyze them collectively.

    **Here is the SQL content from multiple files:**
    {sql_text}

    **Expected Output Format (CSV-like, comma-separated):**
    target_table,target_column,source_table,source_column,mapping_logic
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an expert in SQL lineage extraction."},
                  {"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY
    )

    return response["choices"][0]["message"]["content"]

# Read SQL files (combining them)
sql_text = read_sql_files(sql_file_paths)

# Call GPT-4 for lineage extraction
lineage_text = get_column_lineage(sql_text, TARGET_TABLE, TARGET_COLUMN)

# Convert extracted lineage to DataFrame
lineage_lines = lineage_text.strip().split("\n")[1:]  # Skip the header
lineage_records = [line.split(",") for line in lineage_lines]

df_lineage = pd.DataFrame(lineage_records, columns=["target_table", "target_column", "source_table", "source_column", "mapping_logic"])

# Save to CSV
output_csv_path = "multi_stored_proc_lineage.csv"
df_lineage.to_csv(output_csv_path, index=False)

# Display results
print("\nExtracted Multi-Stored Procedure Lineage:")
print(df_lineage)

print(f"\nLineage saved to: {output_csv_path}")
