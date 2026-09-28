/* ============================================================
   Create CDR File Load Log Table
   ------------------------------------------------------------
   Purpose:
   Track every CDR file processed by the ingestion pipeline,
   including load status, number of rows loaded, and timestamp.
   ============================================================ */

USE telecom_source_db;
GO


/* ------------------------------------------------------------
   Create file load tracking table
   ------------------------------------------------------------ */

CREATE TABLE dbo.file_load_log (
    file_name VARCHAR(255) PRIMARY KEY,
    load_status VARCHAR(20),
    rows_loaded INT NULL,
    load_timestamp DATETIME2 DEFAULT SYSDATETIME()
);
GO


/* ------------------------------------------------------------
   Validate table contents
   ------------------------------------------------------------ */

SELECT *
FROM dbo.file_load_log;