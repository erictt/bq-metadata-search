#!/bin/bash
# wait-for-db.sh

set -e

host="db"
port="5432"
shift

until PGPASSWORD=bq_metadata_password psql -h "$host" -p "$port" -U "bq_metadata" -d "bq_metadata" -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - executing command"
exec "$@"
