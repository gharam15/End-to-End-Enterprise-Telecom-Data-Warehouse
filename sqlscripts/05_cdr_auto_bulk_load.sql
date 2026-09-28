/* ============================================================
   CDR Auto Ingestion - SQL Server
   ------------------------------------------------------------
   Purpose:
   Automatically detect new CDR CSV files from the landing folder,
   load them into SQL Server using BULK INSERT,
   and track each processed file in dbo.file_load_log.
   ============================================================ */


/* ------------------------------------------------------------
   1. Enable xp_cmdshell
   Required to read file names from the landing folder.
   ------------------------------------------------------------ */

EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
GO

EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;
GO


/* ------------------------------------------------------------
   2. Verify xp_cmdshell configuration
   ------------------------------------------------------------ */

EXEC sp_configure 'xp_cmdshell';


/* ------------------------------------------------------------
   3. Test access to the CDR landing folder
   Returns all CSV files currently available.
   ------------------------------------------------------------ */

EXEC xp_cmdshell
'dir /b "D:\telecom-data-platform\data\landing\cdr\*.csv"';


/* ------------------------------------------------------------
   4. Switch to the telecom source database
   ------------------------------------------------------------ */

USE telecom_source_db;
GO


/* ============================================================
   5. Create the automated CDR loading stored procedure
   ============================================================ */

CREATE OR ALTER PROCEDURE dbo.usp_load_new_cdr_files
AS
BEGIN

    SET NOCOUNT ON;


    /* --------------------------------------------------------
       Temporary table used to store CSV file names detected
       in the landing folder.
       -------------------------------------------------------- */

    CREATE TABLE #files (
        file_name VARCHAR(255)
    );


    /* --------------------------------------------------------
       Read all CSV file names from the landing folder.
       -------------------------------------------------------- */

    INSERT INTO #files
    EXEC xp_cmdshell
    'dir /b "D:\telecom-data-platform\data\landing\cdr\*.csv"';


    /* --------------------------------------------------------
       Remove NULL values or invalid records returned
       by xp_cmdshell.
       -------------------------------------------------------- */

    DELETE FROM #files
    WHERE file_name IS NULL
       OR file_name NOT LIKE '%.csv';


    /* --------------------------------------------------------
       Variables used during file processing.
       -------------------------------------------------------- */

    DECLARE @file_name VARCHAR(255);
    DECLARE @full_path VARCHAR(500);
    DECLARE @sql NVARCHAR(MAX);

    DECLARE @before_count BIGINT;
    DECLARE @after_count BIGINT;
    DECLARE @rows_loaded BIGINT;


    /* --------------------------------------------------------
       Select only files that have not already been loaded
       successfully.
       -------------------------------------------------------- */

    DECLARE file_cursor CURSOR FOR

    SELECT file_name
    FROM #files

    WHERE file_name NOT IN (

        SELECT file_name
        FROM dbo.file_load_log
        WHERE load_status = 'SUCCESS'
    );


    OPEN file_cursor;

    FETCH NEXT FROM file_cursor INTO @file_name;


    /* --------------------------------------------------------
       Process each new CSV file individually.
       -------------------------------------------------------- */

    WHILE @@FETCH_STATUS = 0
    BEGIN


        /* Build the complete file path. */

        SET @full_path =
            'D:\telecom-data-platform\data\landing\cdr\'
            + @file_name;


        BEGIN TRY


            /* Count existing rows before loading the file. */

            SELECT @before_count = COUNT(*)
            FROM dbo.cdr_usage_raw;


            /* ------------------------------------------------
               Dynamically generate the BULK INSERT statement.
               ------------------------------------------------ */

            SET @sql = '

            BULK INSERT dbo.cdr_usage_raw

            FROM ''' + @full_path + '''

            WITH (
                FIRSTROW = 2,
                FIELDTERMINATOR = '','',
                ROWTERMINATOR = ''0x0a'',
                TABLOCK
            );';


            /* Execute the BULK INSERT. */

            EXEC sp_executesql @sql;


            /* Count rows after the file has been loaded. */

            SELECT @after_count = COUNT(*)
            FROM dbo.cdr_usage_raw;


            /* Calculate the number of rows loaded from this file. */

            SET @rows_loaded =
                @after_count - @before_count;


            /* ------------------------------------------------
               Register the successful file load.
               ------------------------------------------------ */

            INSERT INTO dbo.file_load_log (
                file_name,
                load_status,
                rows_loaded,
                load_timestamp
            )

            VALUES (
                @file_name,
                'SUCCESS',
                @rows_loaded,
                SYSDATETIME()
            );


            PRINT 'Loaded: ' + @file_name;

            PRINT 'Rows loaded: '
                + CAST(@rows_loaded AS VARCHAR(30));


        END TRY


        BEGIN CATCH


            /* ------------------------------------------------
               Register failed file loads.
               ------------------------------------------------ */

            INSERT INTO dbo.file_load_log (
                file_name,
                load_status,
                rows_loaded,
                load_timestamp
            )

            VALUES (
                @file_name,
                'FAILED',
                0,
                SYSDATETIME()
            );


            PRINT 'Failed: ' + @file_name;

            PRINT ERROR_MESSAGE();


        END CATCH;


        FETCH NEXT FROM file_cursor INTO @file_name;

    END;


    /* --------------------------------------------------------
       Cleanup cursor and temporary table.
       -------------------------------------------------------- */

    CLOSE file_cursor;

    DEALLOCATE file_cursor;

    DROP TABLE #files;


END;
GO


/* ============================================================
   6. Manual test
   Run the procedure manually to validate the ingestion process.
   ============================================================ */

EXEC dbo.usp_load_new_cdr_files;


/* ============================================================
   7. Audit validation
   Review the status of all processed files.
   ============================================================ */

SELECT
    file_name,
    load_status,
    rows_loaded,
    load_timestamp

FROM dbo.file_load_log

ORDER BY load_timestamp DESC;