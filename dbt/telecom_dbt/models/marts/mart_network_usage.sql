with cdr as (

    select *
    from {{ ref('fact_cdr_usage') }}

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
        c.date_sk,

        cc.cell_id,
        cc.country_code,

        count(*) as total_records,

        sum(c.sms_in) as total_sms_in,
        sum(c.sms_out) as total_sms_out,

        sum(c.call_in) as total_call_in,
        sum(c.call_out) as total_call_out,

        sum(c.internet_activity) as total_internet_activity,

        sum(c.sms_in + c.sms_out) as total_sms_activity,

        sum(c.call_in + c.call_out) as total_call_activity

    from cdr c

    left join cdr_cell cc
        on c.cdr_cell_sk = cc.cdr_cell_sk

    group by
        c.date_sk,
        cc.cell_id,
        cc.country_code

)

select *
from final
