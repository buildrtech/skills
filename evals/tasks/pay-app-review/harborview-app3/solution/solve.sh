#!/bin/bash
# Reference path for the oracle agent. The reference memo was written by a
# human from the same inputs the agent sees, with the checker's exact output
# pasted in. It doubles as the verifier's known-good fixture.
set -e
mkdir -p /app/output
cp /solution/reference-memo.md /app/output/review-memo.md
