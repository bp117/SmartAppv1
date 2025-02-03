import os
import re
import pandas as pd

# Directory containing SQL files (modify as needed)
sql_file_paths = [
    "path/to/sql_file1.sql",
    "path/to/sql_file2.sql"
]

# Define SQL keywords for identifying queries
SQL_KEYWORDS = ["CREATE PROCEDURE", "CREATE VIEW", "INSERT INTO", "SELECT", "UPDATE", "DELETE", "FROM", "JOIN", "WHERE", "SET", "CALL"]

# Regular expressions for extracting table and column mappings
INSERT_REGEX = re.compile(r"INSERT INTO\s+(\w+)\s*\((.*?)\)\s*SELECT\s+(.*?)\s+FROM\s+(\w+)", re.IGNORECASE)
SELECT_REGEX = re.compile(r"SELECT\s+(.*?)\s+FROM\s+(\w+)", re.IGNORECASE)
JOIN_REGEX = re.compile(r"JOIN\s+(\w+)\s+ON\s+(\w+\.\w+)\s*=\s*(\w+\.\w+)", re.IGNORECASE)

# Function to extract SQL statements from files
def extract_sql_statements(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        sql_text = file.read()
    
    # Extract lines containing SQL keywords
    sql_lines = [line.strip() for line in sql_text.split("\n") if any(keyword in line.upper() for keyword in SQL_KEYWORDS)]
    return "\n".join(sql_lines)

# Function to parse SQL statements and extract column lineage
def extract_column_lineage(sql_text):
    lineage_records = []
    
    for match in INSERT_REGEX.finditer(sql_text):
        target_table = match.group(1)
        target_columns = [col.strip() for col in match.group(2).split(",")]
        source_columns = [col.strip() for col in match.group(3).split(",")]
        source_table = match.group(4)

        for tgt_col, src_col in zip(target_columns, source_columns):
            lineage_records.append({
                "target_table": target_table,
                "target_column": tgt_col,
                "source_table": source_table,
                "source_column": src_col,
                "mapping_logic": "Direct Mapping"  # Placeholder, can be extended for transformations
            })

    for match in SELECT_REGEX.finditer(sql_text):
        source_table = match.group(2)
        source_columns = [col.strip() for col in match.group(1).split(",")]
        
        for src_col in source_columns:
            lineage_records.append({
                "target_table": "UNKNOWN_TARGET",  # Needs additional mapping
                "target_column": "UNKNOWN_COLUMN",
                "source_table": source_table,
                "source_column": src_col,
                "mapping_logic": "Direct Mapping"
            })

    for match in JOIN_REGEX.finditer(sql_text):
        source_table = match.group(1)
        left_col, right_col = match.group(2), match.group(3)
        
        lineage_records.append({
            "target_table": "JOIN_RESULT",
            "target_column": left_col.split(".")[1],
            "source_table": source_table,
            "source_column": right_col.split(".")[1],
            "mapping_logic": "Join Condition"
        })

    return lineage_records

# Iterate through SQL files and extract lineage
all_lineage_records = []
for file_path in sql_file_paths:
    print(f"Processing: {file_path}")
    sql_text = extract_sql_statements(file_path)
    lineage_records = extract_column_lineage(sql_text)
    all_lineage_records.extend(lineage_records)

# Convert to DataFrame and save as CSV
df_lineage = pd.DataFrame(all_lineage_records)
df_lineage.to_csv("column_lineage.csv", index=False)

# Display the DataFrame
import ace_tools as tools
tools.display_dataframe_to_user(name="Column Lineage", dataframe=df_lineage)
