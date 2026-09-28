/* ============================================================
   Create Telecom CDR Source Database
   ------------------------------------------------------------
   Purpose:
   Create the SQL Server source database and the raw CDR table
   used to store telecom activity data before downstream ingestion.
   ============================================================ */


/* ------------------------------------------------------------
   1. Create source database
   ------------------------------------------------------------ */

CREATE DATABASE telecom_source_db;
GO


/* ------------------------------------------------------------
   2. Switch to source database
   ------------------------------------------------------------ */

USE telecom_source_db;
GO


/* ------------------------------------------------------------
   3. Create raw CDR table
   Column names match the original source files.
   ------------------------------------------------------------ */

CREATE TABLE dbo.cdr_usage_raw (
    datetime VARCHAR(50),
    CellID INT,
    countrycode INT,
    smsin FLOAT NULL,
    smsout FLOAT NULL,
    callin FLOAT NULL,
    callout FLOAT NULL,
    internet FLOAT NULL
);
GO


/* ------------------------------------------------------------
   4. Validate sample records
   ------------------------------------------------------------ */

SELECT TOP 10 *
FROM dbo.cdr_usage_raw;


/* ------------------------------------------------------------
   5. Validate total row count
   ------------------------------------------------------------ */

SELECT COUNT(*) AS total_rows
FROM dbo.cdr_usage_raw;