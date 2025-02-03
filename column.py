import openai
import pandas as pd

# Define OpenAI API Key (Replace with your actual API key)
OPENAI_API_KEY = "your-api-key"

# Define the target table and column
TARGET_TABLE = "CNI_FACLTY_TO_CC"  # Modify as needed
TARGET_COLUMN = "GUARANTOR_NM"  # Modify as needed

# SQL file path (update with actual path)
sql_file_path = "path/to/your/sql_file.sql"

# Function to read the SQL file
def read_sql_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        return file.read()

# Function to query GPT-4 for lineage extraction
def get_column_lineage(sql_text, target_table, target_column):
    prompt = f"""
    You are an expert in SQL lineage analysis and data provenance. Your task is to analyze a given SQL file
    containing stored procedures and views. Identify the lineage for the column '{target_column}' in the table '{target_table}'.
    Trace the lineage back to the source tables and columns, including any joins, transformations, and procedures.

    The SQL file contents are provided below:
    {sql_text}

    Output the lineage in the following structured format (CSV-like):
    target_table,target_column,source_table,source_column,mapping_logic
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an expert in SQL lineage extraction."},
                  {"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY
    )

    return response["choices"][0]["message"]["content"]

# Read SQL file
sql_text = read_sql_file(sql_file_path)

# Get column lineage from GPT-4
lineage_text = get_column_lineage(sql_text, TARGET_TABLE, TARGET_COLUMN)

# Convert extracted lineage to DataFrame
lineage_lines = lineage_text.strip().split("\n")[1:]  # Skip the header
lineage_records = [line.split(",") for line in lineage_lines]

df_lineage = pd.DataFrame(lineage_records, columns=["target_table", "target_column", "source_table", "source_column", "mapping_logic"])

# Save to CSV
output_csv_path = "column_lineage.csv"
df_lineage.to_csv(output_csv_path, index=False)

# Display results
print("\nExtracted Column Lineage:")
print(df_lineage)

print(f"\nLineage saved to: {output_csv_path}")
