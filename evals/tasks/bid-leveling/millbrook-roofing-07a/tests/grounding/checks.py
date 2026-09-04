"""Grounding: what share of the dollar figures in the comparison trace to the
agent's inputs or to the leveling arithmetic on them?

The allowed set is built at verify time from the files under /app/input and
from the script's own output on the hidden extractions, plus pairwise sums
and differences of those numbers so base bid + plugs + adjustments is not
penalised. Figures outside that set count as unsupported. This is a soft
score; the hard version of the same idea is the boundaries gate.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import allowed_amounts, comparison_text, stated_amounts  # noqa: E402


@criterion(description="share of dollar amounts that trace to the inputs or to leveling arithmetic")
def amounts_are_grounded(workspace: Path) -> float:
    text = comparison_text(workspace)
    if not text:
        return 0.0
    stated = stated_amounts(text)
    if not stated:
        return 0.0
    allowed = allowed_amounts(workspace)
    return sum(1 for n in stated if n in allowed) / len(stated)


rk.amounts_are_grounded(weight=1.0)
