with customers as (

    select *
    from {{ ref('dim_customer') }}

),

final as (

    select
        contract,
        internet_service,

        count(*) as total_customers,

        count(*) filter (
            where churn_value = 1
        ) as churned_customers,

        count(*) filter (
            where churn_value = 0
        ) as active_customers,

        round(
            100.0
            * count(*) filter (where churn_value = 1)
            / nullif(count(*), 0),
            2
        ) as churn_rate,

        round(
            avg(monthly_charges)::numeric,
            2
        ) as avg_monthly_charges,

        round(
            avg(tenure_months)::numeric,
            2
        ) as avg_tenure_months,

        round(
            avg(churn_score)::numeric,
            2
        ) as avg_churn_score,

        round(
            avg(cltv)::numeric,
            2
        ) as avg_cltv

    from customers

    group by
        contract,
        internet_service

)

select *
from final