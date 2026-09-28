select *
from {{ ref('fact_billing') }}
where monthly_charges < 0
   or total_amount < 0
   or late_fee < 0