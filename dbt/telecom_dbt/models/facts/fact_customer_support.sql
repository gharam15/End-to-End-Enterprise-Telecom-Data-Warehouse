with support as (

    select *
    from {{ ref('stg_customer_support') }}

),

support_category as (

    select
        support_category_sk,
        ticket_type,
        ticket_priority,
        ticket_channel
    from {{ ref('dim_support_category') }}

),

final as (

    select
        s.ticket_id,

        sc.support_category_sk,

        to_char(
            s.date_of_purchase::timestamp,
            'YYYYMMDD'
        )::integer as purchase_date_sk,

        s.customer_age,
        s.customer_gender,
        s.product_purchased,

        s.ticket_subject,
        s.ticket_description,
        s.ticket_status,
        s.resolution,

        s.first_response_time,
        s.time_to_resolution,
        s.customer_satisfaction_rating,

        s.ingestion_timestamp

    from support s

    left join support_category sc
        on s.ticket_type = sc.ticket_type
       and s.ticket_priority = sc.ticket_priority
       and s.ticket_channel = sc.ticket_channel

)

select *
from final