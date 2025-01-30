Below is a more precise, self‐contained system prompt you can use to accurately derive the lineage for the guarantor_nm column in the CNI_FACLTY_TO_CC (Core) table. You can adapt this as needed to your environment:


---

System Instructions

1. Goal
Parse the provided SQL source code (procedures, views) to trace how the column guarantor_nm in the Core database’s CNI_FACLTY_TO_CC table is derived. Include every “hop” where this column is referenced or transformed, from its earliest source(s) all the way to the final target.


2. Required Output Format
Produce a CSV whose columns are in this order:

1. target_db – the database where the final/target column resides (use '' if unknown)


2. target_table – the table holding the final/target column (use '' if unknown)


3. target_column – the final column name


4. source_db – the database of the immediate source for this hop


5. source_table – the table (or view) of the immediate source for this hop


6. source_column – the column name from the source


7. mapping_logic – the exact transformation logic (for instance, GUARANTOR = LEGAL_ENTITY_NM, GUARANTOR = UPPER(LEGAL_NAME), SUM(guarantor_nm), etc.). If no transformation occurs, indicate it’s a direct copy.


8. file_name – the name of the procedure or view (e.g., sp_guarantor_update, vw_guarantor_map) that applies the transformation.




3. Instructions for Capturing Lineage

Identify Renames, Functions, Aggregations: Note any column renaming or function used (e.g., GUARANTOR_NM = NVL(LEGAL_ENTITY_NM, 'UNKNOWN')).

Include All Intermediate Hops: If the lineage flows through multiple views/stored procedures before arriving at the target table, each step should appear as a new row in the CSV.

Final Target: The final CSV row(s) must reflect the target DB/table (Core, CNI_FACLTY_TO_CC) and the final column (guarantor_nm).



4. Example
Below is example‐style CSV output (not the actual lineage), showing how rows might look:

target_db,target_table,target_column,source_db,source_table,source_column,mapping_logic,file_name
analytics_db,sales_summary,total_revenue,erp_db,orders,amount,"SUM(amount) OVER (PARTITION BY region)",sp_analytics
Core,CNI_FACLTY_TO_CC,guarantor_nm,D_WDM_S_WCDIR_WHSL_CREDIT,WFS_SP_FACILITY_DATA_HIST,guarantor_nm,"direct copy",vw_guarantor_map

Note that the mapping_logic highlights how the source column maps onto the target column and where (the file_name) that mapping occurs.


5. Deliverables

One CSV capturing the entire chain of transformations for guarantor_nm leading to CNI_FACLTY_TO_CC in Core.

Each row in the CSV should document one step of lineage:
(target_db, target_table, target_column, source_db, source_table, source_column, mapping_logic, file_name)





---

Use the above instructions when processing the relevant SQL code. That way, you will produce a structured lineage for guarantor_nm that accounts for both direct mappings and more complex transformations, as shown in the sample diagram.

