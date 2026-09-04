"""Grounding: what share of the document's dollar figures trace to the
user's export?

The allowed set is built at verify time from the two input files and the
hidden fixture's arithmetic, plus pairwise sums and differences so a
legitimate derived figure is not penalized. This is the soft companion to
the boundaries gate: the gate asks for all of them, this reports the share.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import allowed_amounts, document_amounts  # noqa: E402


@criterion(description="share of dollar figures in the document that trace to the export")
def amounts_are_grounded(workspace: Path) -> float:
    printed = document_amounts(workspace)
    if not printed:
        return 0.0
    allowed = allowed_amounts(workspace)
    return sum(1 for n in printed if n in allowed) / len(printed)


rk.amounts_are_grounded(weight=1.0)
