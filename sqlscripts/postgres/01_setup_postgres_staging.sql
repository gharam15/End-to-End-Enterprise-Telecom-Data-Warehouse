/* ============================================================
   PostgreSQL Staging Setup
   ------------------------------------------------------------
   Purpose:
   Create the staging schema and all staging tables used by
   the telecom data platform.
   ============================================================ */


/* ------------------------------------------------------------
   1. Create staging schema
   ------------------------------------------------------------ */

CREATE SCHEMA IF NOT EXISTS staging;


/* ------------------------------------------------------------
   2. Network staging table
   ------------------------------------------------------------ */

CREATE TABLE IF NOT EXISTS staging.network_cells (
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    mcc INTEGER,
    mnc INTEGER,
    lac INTEGER,
    cellid BIGINT,
    average_signal_strength DOUBLE PRECISION,
    range INTEGER,
    samples INTEGER,
    changeable INTEGER,
    radio VARCHAR(20),
    rnc INTEGER,
    cid BIGINT,
    tac INTEGER,
    sid INTEGER,
    nid INTEGER,
    bid INTEGER,
    ingestion_timestamp TIMESTAMPTZ
);


/* ------------------------------------------------------------
   3. CRM customer staging table
   ------------------------------------------------------------ */

CREATE TABLE IF NOT EXISTS staging.customers (
    customerid VARCHAR(50),
    count INTEGER,
    country VARCHAR(100),
    state VARCHAR(100),
    city VARCHAR(150),
    zip_code INTEGER,
    lat_long VARCHAR(100),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    gender VARCHAR(20),
    senior_citizen VARCHAR(20),
    partner VARCHAR(20),
    dependents VARCHAR(20),
    tenure_months INTEGER,
    phone_service VARCHAR(30),
    multiple_lines VARCHAR(50),
    internet_service VARCHAR(50),
    online_security VARCHAR(50),
    online_backup VARCHAR(50),
    device_protection VARCHAR(50),
    tech_support VARCHAR(50),
    streaming_tv VARCHAR(50),
    streaming_movies VARCHAR(50),
    contract VARCHAR(50),
    paperless_billing VARCHAR(20),
    payment_method VARCHAR(100),
    monthly_charges DOUBLE PRECISION,
    total_charges DOUBLE PRECISION,
    churn_label VARCHAR(20),
    churn_value INTEGER,
    churn_score INTEGER,
    cltv INTEGER,
    churn_reason VARCHAR(255),
    ingestion_timestamp TIMESTAMPTZ
);


/* ------------------------------------------------------------
   4. CDR staging table
   ------------------------------------------------------------ */

CREATE TABLE IF NOT EXISTS staging.cdr_usage (
    datetime VARCHAR(50),
    cellid INTEGER,
    countrycode INTEGER,
    smsin DOUBLE PRECISION,
    smsout DOUBLE PRECISION,
    callin DOUBLE PRECISION,
    callout DOUBLE PRECISION,
    internet DOUBLE PRECISION,
    ingestion_timestamp TIMESTAMPTZ
);


/* ------------------------------------------------------------
   5. Billing staging table
   ------------------------------------------------------------ */

CREATE TABLE IF NOT EXISTS staging.billing (
    billing_id BIGINT,
    customer_id VARCHAR(50),
    invoice_date DATE,
    due_date DATE,
    billing_period VARCHAR(20),
    monthly_charges DOUBLE PRECISION,
    total_amount DOUBLE PRECISION,
    payment_status VARCHAR(30),
    payment_method VARCHAR(100),
    late_fee DOUBLE PRECISION,
    contract VARCHAR(50),
    created_at TIMESTAMPTZ,
    ingestion_timestamp TIMESTAMPTZ
);


/* ------------------------------------------------------------
   6. Customer support staging table
   ------------------------------------------------------------ */

CREATE TABLE IF NOT EXISTS staging.customer_support (
    ticket_id BIGINT,
    customer_name VARCHAR(150),
    customer_email VARCHAR(255),
    customer_age INTEGER,
    customer_gender VARCHAR(20),
    product_purchased VARCHAR(150),
    date_of_purchase TIMESTAMP,
    ticket_type VARCHAR(100),
    ticket_subject VARCHAR(255),
    ticket_description TEXT,
    ticket_status VARCHAR(50),
    resolution TEXT,
    ticket_priority VARCHAR(50),
    ticket_channel VARCHAR(50),
    first_response_time TIMESTAMP NULL,
    time_to_resolution TIMESTAMP NULL,
    customer_satisfaction_rating DOUBLE PRECISION NULL,
    ingestion_timestamp TIMESTAMPTZ
);


/* ------------------------------------------------------------
   7. Validate staging tables
   ------------------------------------------------------------ */

SELECT
    table_schema,
    table_name
FROM information_schema.tables
WHERE table_schema = 'staging'
ORDER BY table_name;