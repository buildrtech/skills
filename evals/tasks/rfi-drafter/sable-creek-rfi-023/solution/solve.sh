#!/bin/bash
# Reference path for the oracle agent. The reference RFI was written by a
# human from the same inputs the agent sees, following the skill's
# references/rfi-template.md. It doubles as the verifier's known-good fixture.
set -e
mkdir -p /app/output
cp /solution/reference-rfi-023.md /app/output/rfi-023.md
