#!/bin/bash

# Wait for PostgreSQL to be ready
./wait-for-it.sh postgres:5432 --timeout=60 --strict -- echo "PostgreSQL is up - executing command"

# Apply database migrations
python manage.py migrate

# Apply project fixtures
python manage.py loaddata fixtures/users.yaml

# Apply app specific fixtures
python manage.py loaddata shop/fixtures/customers.yaml
python manage.py loaddata shop/fixtures/products.yaml


# Run the main container command
exec "$@"
