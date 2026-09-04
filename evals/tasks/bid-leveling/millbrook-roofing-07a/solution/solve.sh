#!/bin/bash
# Reference path for the oracle agent. The reference comparison was written by
# a human from the same inputs the agent sees, with the script's exact output
# pasted in. It doubles as the verifier's known-good fixture.
set -e
mkdir -p /app/output
cp /solution/reference-leveled-comparison.md /app/output/leveled-comparison.md
