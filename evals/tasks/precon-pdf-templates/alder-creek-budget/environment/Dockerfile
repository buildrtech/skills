# Python 3.12 for the verifier (harbor-rewardkit needs >= 3.12; Debian
# bookworm only ships 3.11) plus Node 20 for the skill's render.mjs.
FROM node:20-bookworm-slim AS node
FROM python:3.12-slim-bookworm

# Agent-visible environment only. Never copy Task.md, tests/, or solution/ here.
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/npm
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl git ca-certificates bash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY input/ /app/input/
RUN mkdir -p /app/output
