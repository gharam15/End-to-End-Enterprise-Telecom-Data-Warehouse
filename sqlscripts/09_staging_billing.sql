/* ============================================================
   Create Billing Staging Table
   ============================================================ */

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