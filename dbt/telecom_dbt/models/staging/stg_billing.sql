select
    billing_id,
    customer_id,
    invoice_date,
    due_date,
    billing_period,
    monthly_charges,
    total_amount,
    payment_status,
    payment_method,
    late_fee,
    contract,
    created_at,
    ingestion_timestamp
from {{ source('telecom_staging', 'billing') }}