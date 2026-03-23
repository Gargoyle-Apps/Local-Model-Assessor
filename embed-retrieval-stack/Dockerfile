# PostgreSQL + Apache AGE (from official image) + pgvector (built from source).
# Pins: see versions.lock.yaml

ARG AGE_IMAGE=apache/age
ARG AGE_TAG=release_PG18_1.7.0
FROM ${AGE_IMAGE}:${AGE_TAG}

USER root

ARG PGVECTOR_REF=v0.8.0

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        build-essential \
        postgresql-server-dev-18 \
    && git clone --branch "${PGVECTOR_REF}" --depth 1 https://github.com/pgvector/pgvector.git /tmp/pgvector \
    && make -C /tmp/pgvector PG_CONFIG=/usr/lib/postgresql/18/bin/pg_config \
    && make -C /tmp/pgvector install PG_CONFIG=/usr/lib/postgresql/18/bin/pg_config \
    && rm -rf /tmp/pgvector \
    && apt-get purge -y git build-essential postgresql-server-dev-18 \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Runs after base image's 00-create-extension-age.sql (alphabetical order).
COPY init/01-vector.sql /docker-entrypoint-initdb.d/01-vector.sql
COPY init/02-schema.sql /docker-entrypoint-initdb.d/02-schema.sql

USER postgres
