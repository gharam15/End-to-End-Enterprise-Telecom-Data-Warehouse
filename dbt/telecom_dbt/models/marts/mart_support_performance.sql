with support as (

    select *
    from {{ ref('fact_customer_support') }}

),

category as (

    select
        support_category_sk,
        ticket_type,
        ticket_priority,
        ticket_channel
    from {{ ref('dim_support_category') }}

),

final as (

    select
        s.purchase_date_sk,

        c.ticket_type,
        c.ticket_priority,
        c.ticket_channel,

        count(*) as total_tickets,

        count(*) filter (
            where s.ticket_status = 'Closed'
        ) as closed_tickets,

        count(*) filter (
            where s.ticket_status = 'Open'
        ) as open_tickets,

        count(*) filter (
            where s.ticket_status = 'Pending Customer Response'
        ) as pending_tickets,

        round(
            avg(s.customer_satisfaction_rating)::numeric,
            2
        ) as avg_customer_satisfaction

    from support s

    left join category c
        on s.support_category_sk = c.support_category_sk

    group by
        s.purchase_date_sk,
        c.ticket_type,
        c.ticket_priority,
        c.ticket_channel

)

select *
from final