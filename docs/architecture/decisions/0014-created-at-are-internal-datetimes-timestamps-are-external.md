# 14. created_at are internal datetimes, timestamps are external

Date: 2024-05-30

## Who creates the piece of data matters as much as when

Several entities and value objects in the domain contain creation dates.

PaymentOperation and PaymentAttempt are entities, with their own id and creation date. Others, like Token or Transaction,
contain timestamps, because this system is not in control as to when those value objects get created (they belong to third party systems).

The clear cut naming different is there to ensure the distinction is explicit at all times.