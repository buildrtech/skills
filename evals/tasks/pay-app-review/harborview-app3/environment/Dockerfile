FROM python:3.12-slim-bookworm

# Agent-visible environment only. Never copy Task.md, tests/, or solution/ here.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl git ca-certificates bash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY input/ /app/input/
RUN mkdir -p /app/output
