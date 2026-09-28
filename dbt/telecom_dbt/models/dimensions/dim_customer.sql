with source as (

    select *
    from {{ ref('stg_customers') }}

),

final as (

    select
        row_number() over (order by customer_id) as customer_sk,

        customer_id,
        gender,
        senior_citizen,
        partner,
        dependents,
        tenure_months,

        country,
        state,
        city,
        zip_code,
        latitude,
        longitude,

        phone_service,
        multiple_lines,
        internet_service,
        online_security,
        online_backup,
        device_protection,
        tech_support,
        streaming_tv,
        streaming_movies,

        contract,
        paperless_billing,
        payment_method,

        monthly_charges,
        total_charges,

        churn_label,
        churn_value,
        churn_score,
        cltv,
        churn_reason,

        ingestion_timestamp

    from source

)

select *
from final