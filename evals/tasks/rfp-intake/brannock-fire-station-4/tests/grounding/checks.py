"""Grounding: what share of the dates and dollar amounts in the review appear
in the package the agent was given?

The allowed sets are built at verify time from the two agent-visible input
files (plus the date the instruction says the package arrived). This is the
soft version of the boundary gates: the gates ask whether anything at all was
invented, this asks how much of the review is traceable.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import (  # noqa: E402
    allowed_dates,
    amounts_in,
    date_allowed,
    dates_in,
    input_text,
    memo_text,
)


@criterion(description="share of dates in the review that appear in the package")
def dates_are_grounded(workspace: Path) -> float:
    found = dates_in(memo_text(workspace))
    if not found:
        return 0.0
    allowed = allowed_dates(workspace)
    return sum(1 for d in found if date_allowed(d, allowed)) / len(found)


@criterion(description="share of dollar-scale amounts in the review that appear in the package")
def amounts_are_grounded(workspace: Path) -> float:
    found = amounts_in(memo_text(workspace))
    if not found:
        return 0.0
    allowed = amounts_in(input_text(workspace))
    return sum(1 for n in found if n in allowed) / len(found)


rk.dates_are_grounded(weight=1.0)
rk.amounts_are_grounded(weight=1.0)
