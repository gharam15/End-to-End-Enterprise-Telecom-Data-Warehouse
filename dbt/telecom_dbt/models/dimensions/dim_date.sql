with date_spine as (

    select generate_series(
        date '2013-01-01',
        date '2030-12-31',
        interval '1 day'
    )::date as full_date

),

final as (

    select
        to_char(full_date, 'YYYYMMDD')::integer as date_sk,
        full_date,
        extract(day from full_date)::integer as day,
        extract(month from full_date)::integer as month,
        trim(to_char(full_date, 'Month')) as month_name,
        extract(quarter from full_date)::integer as quarter,
        extract(year from full_date)::integer as year,
        extract(isodow from full_date)::integer as day_of_week,
        trim(to_char(full_date, 'Day')) as day_name,
        case
            when extract(isodow from full_date) in (6, 7)
                then true
            else false
        end as is_weekend

    from date_spine

)

select *
from final