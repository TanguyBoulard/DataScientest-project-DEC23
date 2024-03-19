FROM postgres:15.1-alpine

LABEL author="djibi"
LABEL description="Postgres Image for demo"
LABEL version="1.0"

# Copier les fichiers SQL du répertoire local app/resources/sql vers le répertoire docker-entrypoint-initdb.d dans le conteneur
COPY app/resources/sql/*.sql /docker-entrypoint-initdb.d/