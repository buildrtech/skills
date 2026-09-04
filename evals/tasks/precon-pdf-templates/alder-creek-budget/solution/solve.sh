#!/bin/bash
# Reference path for the oracle agent.
#
# reference-data.json was transcribed by hand from /app/input against the
# budget export schema: every figure is the exported figure, including the
# Division 09 subtotal that does not foot, which is called out in the notes
# and in the QA note rather than corrected.
#
# render.mjs and warm-owner-facing.css are verbatim copies of the skill's
# files so the oracle also runs in the baseline condition, where the skill
# directory is not injected.
set -e
mkdir -p /app/output
cd /solution

if command -v node >/dev/null 2>&1; then
  node render.mjs reference-data.json /app/output/budget-export.html
  node apply-theme.mjs /app/output/budget-export.html warm-owner-facing.css
else
  # No Node in the image: ship the byte-identical pre-rendered document.
  cp reference-budget-export.html /app/output/budget-export.html
fi

cp qa-notes.md /app/output/qa-notes.md
