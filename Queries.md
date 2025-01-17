Based on the context of your database and the information provided, here are some possible metrics that can be displayed in a Grafana dashboard for executive reporting, along with the SQL queries to generate them:


---

1. Overall File Processing Status

Metric:

Total files processed

Files processed successfully, failed, and ignored


SQL Query:

SELECT 
    STATUS, 
    COUNT(*) AS FILE_COUNT 
FROM 
    AIDA.GROUP_TO_FILE_MAPPING 
GROUP BY 
    STATUS;


---

2. Facility-Wise Processing Status

Metric:

Facility ID-wise count of files in each status (e.g., Success, Failed)


SQL Query:

SELECT 
    FACILITY_ID, 
    STATUS, 
    COUNT(*) AS FILE_COUNT 
FROM 
    AIDA.GROUP_TO_FILE_MAPPING 
GROUP BY 
    FACILITY_ID, STATUS;


---

3. Average Processing Time Per File

Metric:

Average execution time for processing files


SQL Query:

SELECT 
    AVG(EXEC_DURATION) AS AVG_EXECUTION_TIME 
FROM 
    AIDA.GROUP_TO_FILE_MAPPING
WHERE 
    STATUS IN ('SUCCESS', 'FAILED');


---

4. Facility Execution Status

Metric:

Facility execution status summary (e.g., total facilities, success, failed, not started)


SQL Query:

SELECT 
    STATUS, 
    COUNT(*) AS FACILITY_COUNT 
FROM 
    AIDA.FACILITY_EXECUTION_STATUS 
GROUP BY 
    STATUS;


---

5. Facility-Wise File Count

Metric:

Number of files per facility


SQL Query:

SELECT 
    FACILITY_ID, 
    COUNT(*) AS FILE_COUNT 
FROM 
    AIDA.GROUP_TO_FILE_MAPPING 
GROUP BY 
    FACILITY_ID;


---

6. Error Summary

Metric:

Count of files with specific error descriptions


SQL Query:

SELECT 
    ERROR_DESC, 
    COUNT(*) AS FILE_COUNT 
FROM 
    AIDA.GROUP_TO_FILE_MAPPING 
WHERE 
    STATUS = 'FAILED' 
GROUP BY 
    ERROR_DESC;


---

7. Comparison Stats

Metric:

Total matched and unmatched fields for all facilities


SQL Query:

SELECT 
    FACILITY_ID, 
    SUM(MATCHED_FIELDS) AS TOTAL_MATCHED, 
    SUM(UNMATCHED_FIELDS) AS TOTAL_UNMATCHED 
FROM 
    AIDA.PROCESS_STATS 
GROUP BY 
    FACILITY_ID;


---

8. Files Processed Over Time

Metric:

Number of files processed per day


SQL Query:

SELECT 
    CAST(CREATION_TIMESTAMP AS DATE) AS PROCESS_DATE, 
    COUNT(*) AS FILE_COUNT 
FROM 
    AIDA.GROUP_TO_FILE_MAPPING 
GROUP BY 
    CAST(CREATION_TIMESTAMP AS DATE)
ORDER BY 
    PROCESS_DATE;


---

9. Facility Processing Time

Metric:

Average execution time per facility


SQL Query:

SELECT 
    FACILITY_ID, 
    AVG(EXEC_DURATION) AS AVG_EXECUTION_TIME 
FROM 
    AIDA.FACILITY_EXECUTION_STATUS 
WHERE 
    STATUS IN ('SUCCESS', 'FAILED') 
GROUP BY 
    FACILITY_ID;


---

10. Facilities with Highest Failure Rate

Metric:

Facilities with the most failed files


SQL Query:

SELECT 
    FACILITY_ID, 
    COUNT(*) AS FAILED_COUNT 
FROM 
    AIDA.GROUP_TO_FILE_MAPPING 
WHERE 
    STATUS = 'FAILED' 
GROUP BY 
    FACILITY_ID 
ORDER BY 
    FAILED_COUNT DESC 
LIMIT 10;


---

11. Pending Files per Facility

Metric:

Number of files not processed (status: not started) per facility


SQL Query:

SELECT 
    FACILITY_ID, 
    COUNT(*) AS PENDING_FILE_COUNT 
FROM 
    AIDA.GROUP_TO_FILE_MAPPING 
WHERE 
    STATUS = 'NOT_STARTED' 
GROUP BY 
    FACILITY_ID;


---

12. Success Rate Percentage

Metric:

Percentage of successfully processed files for all facilities


SQL Query:

SELECT 
    FACILITY_ID, 
    ROUND((SUM(CASE WHEN STATUS = 'SUCCESS' THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS SUCCESS_RATE 
FROM 
    AIDA.GROUP_TO_FILE_MAPPING 
GROUP BY 
    FACILITY_ID;


---

13. Failed Files with High Retry Count

Metric:

Files that failed after the maximum retry attempts


SQL Query:

SELECT 
    FACILITY_ID, 
    FILE_NAME, 
    RETRY_COUNT 
FROM 
    AIDA.GROUP_TO_FILE_MAPPING 
WHERE 
    STATUS = 'FAILED' 
AND 
    RETRY_COUNT = (SELECT MAX(RETRY_COUNT) FROM AIDA.GROUP_TO_FILE_MAPPING);


---

14. Comparison Stats Accuracy Rate

Metric:

Accuracy rate based on matched vs unmatched fields


SQL Query:

SELECT 
    FACILITY_ID, 
    ROUND((SUM(MATCHED_FIELDS) * 100.0) / (SUM(MATCHED_FIELDS) + SUM(UNMATCHED_FIELDS)), 2) AS ACCURACY_RATE 
FROM 
    AIDA.PROCESS_STATS 
GROUP BY 
    FACILITY_ID;


---

15. Total Processing Time Across All Files

Metric:

Total execution duration for all files


SQL Query:

SELECT 
    SUM(EXEC_DURATION) AS TOTAL_EXECUTION_TIME 
FROM 
    AIDA.GROUP_TO_FILE_MAPPING;


---

These metrics provide insights into the status and efficiency of your file processing pipeline, facilities, error occurrences, and overall system performance. Let me know if you need further customization or additional queries!

