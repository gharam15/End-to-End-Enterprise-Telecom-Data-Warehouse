with source as (

    select
        cell_id,
        country_code
    from {{ ref('stg_cdr_usage') }}

),

distinct_cells as (

    select distinct
        cell_id,
        country_code
    from source

),

final as (

    select
        row_number() over (
            order by cell_id, country_code
        ) as cdr_cell_sk,

        cell_id,
        country_code

    from distinct_cells

)

select *
from final