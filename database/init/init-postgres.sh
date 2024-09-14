#!/bin/bash
set -e

echo "Starting PostgreSQL initialization script..."

# Function to hash password using openssl
hash_password() {
    password="$1"
    salt=$(openssl rand -base64 16)
    hashed=$(echo -n "$password$salt" | openssl dgst -binary -sha512 | openssl enc -base64 -A)
    echo "$hashed:$salt"
}

echo "Hashing passwords..."
# Hash passwords
hashed_api_admin_password=$(hash_password "$API_ADMIN_PASSWORD")
hashed_api_password=$(hash_password "$API_PASSWORD")

# Escape special characters in hashed passwords
hashed_api_admin_password_escaped=$(echo "$hashed_api_admin_password" | sed 's/[\/&]/\\&/g')
hashed_api_password_escaped=$(echo "$hashed_api_password" | sed 's/[\/&]/\\&/g')

echo "Replacing placeholders in SQL file..."
# Replace placeholders in SQL file
sed -e "s/\${PG_USER}/$PG_USER/" \
    -e "s/\${PG_PASSWORD}/$PG_PASSWORD/" \
    -e "s/\${POSTGRES_DB}/$POSTGRES_DB/" \
    -e "s/\${API_ADMIN_USER}/$API_ADMIN_USER/" \
    -e "s/\${API_ADMIN_PASSWORD}/$hashed_api_admin_password_escaped/" \
    -e "s/\${API_USER}/$API_USER/" \
    -e "s/\${API_PASSWORD}/$hashed_api_password_escaped/" \
    -e "s/\${AIRFLOW_DB}/$AIRFLOW_DB/" \
    -e "s/\${AIRFLOW_USER}/$AIRFLOW_USER/" \
    -e "s/\${AIRFLOW_PASSWORD}/$AIRFLOW_PASSWORD/" \
    -e "s/\${AIRFLOW_ADMIN_USER}/$AIRFLOW_ADMIN_USER/" \
    -e "s/\${AIRFLOW_ADMIN_PASSWORD}/$AIRFLOW_ADMIN_PASSWORD/" \
    /tmp/init-postgres-tmp.sql > /tmp/init-postgres.sql

echo "Executing SQL file..."
# Execute SQL file
if psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /tmp/init-postgres.sql; then
    echo "PostgreSQL initialization completed successfully."
else
    echo "Error: PostgreSQL initialization failed."
    exit 1
fi