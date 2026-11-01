#!/bin/bash
# Crea bases y usuarios por servicio. Se ejecuta solo en el primer arranque.
set -euo pipefail
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<SQL
CREATE USER hipomaster WITH PASSWORD '${HIPO_DB_PASSWORD}';
CREATE USER litellm    WITH PASSWORD '${LITELLM_DB_PASSWORD}';
CREATE USER langfuse   WITH PASSWORD '${LANGFUSE_DB_PASSWORD}';
CREATE USER scraper    WITH PASSWORD '${SCRAPER_DB_PASSWORD}';
CREATE DATABASE hipomaster OWNER hipomaster;
CREATE DATABASE litellm    OWNER litellm;
CREATE DATABASE langfuse   OWNER langfuse;
\c hipomaster
CREATE EXTENSION IF NOT EXISTS vector;
CREATE SCHEMA IF NOT EXISTS ofertas AUTHORIZATION hipomaster;
GRANT USAGE ON SCHEMA ofertas TO scraper;
ALTER DEFAULT PRIVILEGES FOR ROLE hipomaster IN SCHEMA ofertas
  GRANT SELECT, INSERT, UPDATE ON TABLES TO scraper;
SQL
