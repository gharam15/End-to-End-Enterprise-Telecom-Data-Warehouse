with billing as (

    select *
    from {{ ref('stg_billing') }}

),

customer as (

    select
        customer_sk,
        customer_id
    from {{ ref('dim_customer') }}

),

final as (

    select
        b.billing_id,

        c.customer_sk,

        to_char(b.invoice_date, 'YYYYMMDD')::integer as invoice_date_sk,
        to_char(b.due_date, 'YYYYMMDD')::integer as due_date_sk,

        b.billing_period,
        b.monthly_charges,
        b.total_amount,
        b.late_fee,
        b.payment_status,
        b.payment_method,
        b.contract,

        b.created_at,
        b.ingestion_timestamp

    from billing b

    left join customer c
        on b.customer_id = c.customer_id

)

select *
from final