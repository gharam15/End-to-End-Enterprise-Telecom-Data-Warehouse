select *
from {{ ref('fact_customer_support') }}
where
    (
        customer_age is not null
        and (customer_age <= 0 or customer_age > 120)
    )
    or
    (
        customer_satisfaction_rating is not null
        and (
            customer_satisfaction_rating < 1
            or customer_satisfaction_rating > 5
        )
    )