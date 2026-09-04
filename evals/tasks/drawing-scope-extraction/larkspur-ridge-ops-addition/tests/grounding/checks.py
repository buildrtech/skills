"""Grounding: what share of the sheet numbers printed in the scope list are
sheets that exist in the G-000 index?

Counted over every sheet-shaped token in the document, in citations and in
prose alike, minus the lines that are reporting a sheet as missing. It is the
graded companion to the boundaries gate, which looks only at citation lines
and is all-or-nothing. This is a soft score, not a gate.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import SHEETS, grounded_lines, scope_text, sheet_ids  # noqa: E402


@criterion(description="share of sheet numbers in the scope list that exist in the sheet index")
def sheet_ids_are_grounded(workspace: Path) -> float:
    text = scope_text(workspace)
    if not text:
        return 0.0
    found = sheet_ids("\n".join(grounded_lines(text)))
    if not found:
        return 0.0
    return sum(1 for s in found if s in SHEETS) / len(found)


rk.sheet_ids_are_grounded(weight=1.0)
