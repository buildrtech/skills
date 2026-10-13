#!/bin/bash
# Reference path for the oracle agent. The reference review uses the
# same inputs the agent sees, following the skill's workflow
# and output template. It doubles as the verifier's known-good fixture.
set -e
mkdir -p /app/output
cp /solution/reference-intake-review.md /app/output/intake-review.md
