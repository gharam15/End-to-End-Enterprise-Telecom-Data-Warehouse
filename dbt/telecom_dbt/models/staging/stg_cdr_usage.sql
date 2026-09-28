select
    datetime as event_datetime,
    cellid as cell_id,
    countrycode as country_code,
    smsin as sms_in,
    smsout as sms_out,
    callin as call_in,
    callout as call_out,
    internet as internet_activity,
    source_file,
    source_loaded_at,
    ingestion_timestamp
from {{ source('telecom_staging', 'cdr_usage') }}