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

-- cheak load
SELECT COUNT(*)
FROM staging.customers;

SELECT *
FROM staging.customers;


