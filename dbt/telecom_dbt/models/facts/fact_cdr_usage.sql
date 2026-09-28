with cdr as (

    select *
    from {{ ref('stg_cdr_usage') }}

),

cdr_cell as (

    select
        cdr_cell_sk,
        cell_id,
        country_code
    from {{ ref('dim_cdr_cell') }}

),

final as (

    select
        row_number() over (
            order by c.event_datetime, c.cell_id, c.country_code
        ) as cdr_sk,

        cc.cdr_cell_sk,

        to_char(
            c.event_datetime::timestamp,
            'YYYYMMDD'
        )::integer as date_sk,

        c.event_datetime,

        c.sms_in,
        c.sms_out,
        c.call_in,
        c.call_out,
        c.internet_activity,

        c.source_file,
        c.source_loaded_at,
        c.ingestion_timestamp

    from cdr c

    left join cdr_cell cc
        on c.cell_id = cc.cell_id
       and c.country_code = cc.country_code

)

select *
from final