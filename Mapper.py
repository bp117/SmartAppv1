import pandas as pd
import cx_Oracle

# Constants
GROUP_ID_RANGE = 50  # Customize the group ID range here

# Oracle Database connection details (replace with your DB parameters)
DB_HOST = "your_host"
DB_PORT = "your_port"
DB_SERVICE = "your_service"
DB_USER = "your_username"
DB_PASSWORD = "your_password"
TABLE_NAME = "AIDA.GROUP_TO_FILE_MAPPING"

def generate_group_ids(num_files, start_group_id, group_id_range):
    """
    Generate group IDs for a facility's files.
    """
    group_ids = []
    for i in range(num_files):
        group_id = (start_group_id + i) % group_id_range
        group_ids.append(group_id)
    return group_ids

def process_and_verify_data(file_path, group_id_range=50):
    """
    Process the Excel data and verify results before database insertion.
    """
    # Read Excel file
    df = pd.read_excel(file_path)

    # Ensure required columns exist
    required_columns = ['FACILITY_ID', 'TRANCHE_ID', 'FILE_NAME', 'FOLDER_PATH', 'DOC_TYPE']
    if not all(column in df.columns for column in required_columns):
        raise ValueError(f"Excel sheet must contain the following columns: {required_columns}")

    # Sort data by FACILITY_ID and FILE_NAME
    df = df.sort_values(by=['FACILITY_ID', 'FILE_NAME']).reset_index(drop=True)

    # Assign Group IDs
    start_group_id = 0  # Initialize starting group ID
    group_ids = []

    for facility_id, facility_group in df.groupby('FACILITY_ID'):
        num_files = len(facility_group)
        facility_group_ids = generate_group_ids(num_files, start_group_id, group_id_range)
        group_ids.extend(facility_group_ids)
        start_group_id = (start_group_id + num_files) % group_id_range

    df['GROUP_ID'] = group_ids

    # Add additional columns for database insertion
    df['STATUS'] = 'NOT_STARTED'  # Default status
    df['RETRY_COUNT'] = 0  # Default retry count
    df['EXEC_DURATION'] = None  # Placeholder for execution duration
    df['ERROR_DESC'] = None  # Placeholder for error description

    # Verify Results
    print("=== Data Summary ===")
    print(f"Total Records: {len(df)}")
    print(f"Unique Facility IDs: {df['FACILITY_ID'].nunique()}")
    print(f"Group ID Distribution:")
    print(df['GROUP_ID'].value_counts().sort_index())

    # Export data to CSV for verification
    output_file = "verified_data.csv"
    df.to_csv(output_file, index=False)
    print(f"Processed data saved to: {output_file}")

    return df

def insert_data_to_db(df):
    """
    Insert verified data into the Oracle database.
    """
    # Connect to the Oracle database
    dsn_tns = cx_Oracle.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE)
    conn = cx_Oracle.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn_tns)
    cursor = conn.cursor()

    # Insert data into the table
    for _, row in df.iterrows():
        query = f"""
        INSERT INTO {TABLE_NAME} (
            GROUP_ID, FACILITY_ID, TRANCHE_ID, FILE_NAME, DOC_TYPE, STATUS, RETRY_COUNT, EXEC_DURATION, ERROR_DESC
        ) VALUES (
            :1, :2, :3, :4, :5, :6, :7, :8, :9
        )
        """
        cursor.execute(query, (
            row['GROUP_ID'],
            row['FACILITY_ID'],
            row['TRANCHE_ID'],
            row['FILE_NAME'],
            row['DOC_TYPE'],
            row['STATUS'],
            row['RETRY_COUNT'],
            row['EXEC_DURATION'],
            row['ERROR_DESC']
        ))

    # Commit and close connection
    conn.commit()
    conn.close()
    print("Data successfully populated into the Oracle database!")

# Main execution
if __name__ == "__main__":
    # Provide the path to your Excel sheet
    excel_file_path = "group_to_file_mapping.xlsx"
    
    # Step 1: Process and verify data
    verified_data = process_and_verify_data(excel_file_path, group_id_range=GROUP_ID_RANGE)
    
    # Step 2: Confirm before inserting into the database
    user_input = input("Do you want to insert the verified data into the database? (yes/no): ").strip().lower()
    if user_input == "yes":
        insert_data_to_db(verified_data)
    else:
        print("Data insertion skipped.")
