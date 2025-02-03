import re
import pandas as pd

# Define the target table and column for lineage extraction
TARGET_TABLE = "CNI_FACLTY_TO_CC"  # Modify as needed
TARGET_COLUMN = "GUARANTOR_NM"  # Modify as needed

# SQL file paths (update with actual paths)
sql_file_paths = [
    "path/to/sql_file1.sql",
    "path/to/sql_file2.sql"
]

# Define SQL patterns to extract table and column relationships
INSERT_REGEX = re.compile(r"INSERT INTO\s+(\w+)\s*\((.*?)\)\s*SELECT\s+(.*?)\s+FROM\s+(\w+)", re.IGNORECASE)
SELECT_REGEX = re.compile(r"SELECT\s+(.*?)\s+FROM\s+(\w+)", re.IGNORECASE)
JOIN_REGEX = re.compile(r"JOIN\s+(\w+)\s+ON\s+(\w+\.\w+)\s*=\s*(\w+\.\w+)", re.IGNORECASE)

def extract_sql_statements(sql_text):
    """Extract SQL statements containing key lineage keywords."""
    sql_keywords = ["CREATE PROCEDURE", "CREATE VIEW", "INSERT INTO", "SELECT", "UPDATE", "DELETE", "FROM", "JOIN", "WHERE", "CALL"]
    return "\n".join([line.strip() for line in sql_text.split("\n") if any(keyword in line.upper() for keyword in sql_keywords)])

def extract_column_lineage(sql_text, target_table, target_column):
    """Extract lineage for the given target table and column."""
    lineage_records = []
    
    for match in INSERT_REGEX.finditer(sql_text):
        tgt_table, tgt_cols, src_cols, src_table = match.groups()
        tgt_columns = [col.strip() for col in tgt_cols.split(",")]
        src_columns = [col.strip() for col in src_cols.split(",")]

        if target_table == tgt_table and target_column in tgt_columns:
            src_index = tgt_columns.index(target_column)
            lineage_records.append({
                "target_table": tgt_table,
                "target_column": target_column,
                "source_table": src_table,
                "source_column": src_columns[src_index],
                "mapping_logic": "Direct Mapping"
            })

    for match in SELECT_REGEX.finditer(sql_text):
        src_cols, src_table = match.groups()
        src_columns = [col.strip() for col in src_cols.split(",")]
        
        if target_column in src_columns:
            lineage_records.append({
                "target_table": target_table,
                "target_column": target_column,
                "source_table": src_table,
                "source_column": target_column,
                "mapping_logic": "Direct Mapping"
            })

    for match in JOIN_REGEX.finditer(sql_text):
        src_table, left_col, right_col = match.groups()

        if f"{target_table}.{target_column}" in [left_col, right_col]:
            source_column = left_col if right_col.endswith(target_column) else right_col
            lineage_records.append({
                "target_table": target_table,
                "target_column": target_column,
                "source_table": src_table,
                "source_column": source_column.split(".")[1],
                "mapping_logic": "Join Condition"
            })

    return lineage_records

# Process each SQL file and extract lineage
all_lineage_records = []
for file_path in sql_file_paths:
    print(f"Processing: {file_path}")
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        sql_text = file.read()
    
    filtered_sql_text = extract_sql_statements(sql_text)
    lineage_records = extract_column_lineage(filtered_sql_text, TARGET_TABLE, TARGET_COLUMN)
    all_lineage_records.extend(lineage_records)

# Convert lineage records to DataFrame
df_lineage = pd.DataFrame(all_lineage_records)

# Save to CSV
output_csv_path = "column_lineage.csv"
df_lineage.to_csv(output_csv_path, index=False)

# Display results
print("\nExtracted Column Lineage:")
print(df_lineage)

print(f"\nLineage saved to: {output_csv_path}")
