#!/bin/bash
# Reference path for the oracle agent. The reference scope list is the output
# of the skill's scope_list.py run on the corrected candidates file, plus the
# coverage report the skill's last workflow step asks for. It doubles as the
# verifier's known-good fixture.
set -e
mkdir -p /app/output
cp /solution/reference-scope-list.md /app/output/scope-list.md
