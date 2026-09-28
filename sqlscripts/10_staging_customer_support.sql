/* ============================================================
   Create Customer Support Staging Table
   ============================================================ */

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