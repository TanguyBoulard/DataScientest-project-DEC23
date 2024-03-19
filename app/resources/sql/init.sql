--CREATE ROLE IF NOT EXISTS jon WITH LOGIN PASSWORD 'dho';

-- Création de la base de données

--GRANT ALL PRIVILEGES ON DATABASE postgres_db TO jon;
-- Créez le rôle d'utilisateur

--CREATE ROLE jon WITH LOGIN PASSWORD 'dho' SUPERUSER;

--CREATE DATABASE test_db WITH OWNER 'ddiop';

-- Créer l'utilisateur avec tous les privilèges
--CREATE USER australia_user WITH PASSWORD 'australia_password';
--ALTER USER australia_user WITH SUPERUSER;

-- Créer la base de données et attribuer l'utilisateur comme propriétaire
--CREATE DATABASE australia_db WITH OWNER australia_user;
--CREATE ROLE australia_user WITH SUPERUSER LOGIN PASSWORD 'australia_password';
--CREATE USER australia_user WITH PASSWORD 'australia_password' CREATEDB CREATEROLE;
--ALTER ROLE postgres WITH SUPERUSER;