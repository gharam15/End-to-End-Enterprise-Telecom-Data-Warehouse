with source as (

    select *
    from {{ ref('stg_customer_support') }}

),

distinct_categories as (

    select distinct
        ticket_type,
        ticket_priority,
        ticket_channel

    from source

),

final as (

    select
        row_number() over (
            order by
                ticket_type,
                ticket_priority,
                ticket_channel
        ) as support_category_sk,

        ticket_type,
        ticket_priority,
        ticket_channel

    from distinct_categories

)

select *
from final