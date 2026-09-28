select *
from {{ ref('fact_cdr_usage') }}
where sms_in < 0
   or sms_out < 0
   or call_in < 0
   or call_out < 0
   or internet_activity < 0