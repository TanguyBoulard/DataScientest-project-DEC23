#!/bin/bash
set -e

# Function to hash password using openssl
hash_password() {
    password="$1"
    salt=$(openssl rand -base64 16)
    hashed=$(echo -n "$password$salt" | openssl dgst -binary -sha512 | openssl enc -base64 -A)
    echo "$hashed:$salt"
}

# Hash passwords
hashed_api_admin_password=$(hash_password "$API_ADMIN_PASSWORD")
hashed_api_password=$(hash_password "$API_PASSWORD")

# Escape special characters in hashed passwords
hashed_api_admin_password_escaped=$(echo "$hashed_api_admin_password" | sed 's/[\/&]/\\&/g')
hashed_api_password_escaped=$(echo "$hashed_api_password" | sed 's/[\/&]/\\&/g')

# Replace placeholders in SQL file
sed -e "s/\${PG_USER}/$PG_USER/" \
    -e "s/\${PG_PASSWORD}/$PG_PASSWORD/" \
    -e "s/\${POSTGRES_DB}/$POSTGRES_DB/" \
    -e "s/\${API_ADMIN_USER}/$API_ADMIN_USER/" \
    -e "s/\${API_ADMIN_PASSWORD}/$hashed_api_admin_password_escaped/" \
    -e "s/\${API_USER}/$API_USER/" \
    -e "s/\${API_PASSWORD}/$hashed_api_password_escaped/" \
    /tmp/init-postgres-tmp.sql > /tmp/init-postgres.sql

# Execute SQL file
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /tmp/init-postgres.sql