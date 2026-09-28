with billing as (

    select *
    from {{ ref('fact_billing') }}

),

date_dim as (

    select
        date_sk,
        full_date
    from {{ ref('dim_date') }}

),

final as (

    select
        b.invoice_date_sk,
        d.full_date as invoice_date,

        count(*) as total_invoices,

        sum(b.total_amount) as total_revenue,

        sum(b.late_fee) as total_late_fees,

        avg(b.monthly_charges) as avg_monthly_charges,

        count(*) filter (
            where b.payment_status = 'Paid'
        ) as paid_invoices,

        count(*) filter (
            where b.payment_status = 'Pending'
        ) as pending_invoices,

        count(*) filter (
            where b.payment_status = 'Late'
        ) as late_invoices

    from billing b

    left join date_dim d
        on b.invoice_date_sk = d.date_sk

    group by
        b.invoice_date_sk,
        d.full_date

)

select *
from final