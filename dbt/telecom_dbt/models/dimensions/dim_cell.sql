with source as (

    select *
    from {{ ref('stg_network_cells') }}

),

deduplicated as (

    select
        *,
        row_number() over (
            partition by cell_id, mcc, mnc, lac
            order by ingestion_timestamp desc
        ) as rn

    from source

),

final as (

    select
        row_number() over (
            order by cell_id, mcc, mnc, lac
        ) as cell_sk,

        cell_id,
        mcc,
        mnc,
        lac,

        lat as latitude,
        lon as longitude,

        radio,
        average_signal_strength,
        range,
        samples,
        changeable,

        rnc,
        cid,
        tac,
        sid,
        nid,
        bid,

        ingestion_timestamp

    from deduplicated

    where rn = 1

)

select *
from final