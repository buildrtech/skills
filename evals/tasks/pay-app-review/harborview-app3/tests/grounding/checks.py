"""Grounding: every dollar amount in the memo traces to the inputs or to
arithmetic the checker performs on them.

The allowed set is built at verify time from the input files and from the
checker's own output on the hidden fixture, plus pairwise differences and
sums of those numbers so legitimate arithmetic is not penalized. Amounts
outside that set count as unsupported. This is a soft score, not a gate.
"""

from __future__ import annotations

import re
import sys
from decimal import Decimal
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import memo_text, norm  # noqa: E402

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "script-output.md"
NUMBER = re.compile(r"(?<![\d.])(\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?(?![\d])")


def _numbers(text: str) -> set[Decimal]:
    out: set[Decimal] = set()
    for m in NUMBER.finditer(text):
        raw = m.group(0).replace(",", "")
        try:
            out.add(Decimal(raw).quantize(Decimal("0.01")))
        except Exception:
            pass
    return out


def _allowed(workspace: Path) -> set[Decimal]:
    sources = [workspace / "input" / f for f in ("cover-sheet.md", "pay-app-2.csv", "pay-app-3.csv")]
    text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in sources if p.is_file())
    if FIXTURE.is_file():
        text += "\n" + FIXTURE.read_text(encoding="utf-8")
    base = _numbers(text)
    big = {n for n in base if n >= 1000}
    derived: set[Decimal] = set()
    for a, b in combinations(sorted(big), 2):
        derived.add(abs(a - b))
        derived.add(a + b)
    for n in big:
        derived.add((n * Decimal("0.10")).quantize(Decimal("0.01")))
        derived.add((n * Decimal("0.05")).quantize(Decimal("0.01")))
    return base | derived


@criterion(description="share of dollar amounts in the memo that trace to inputs or checker arithmetic")
def amounts_are_grounded(workspace: Path) -> float:
    text = norm(memo_text(workspace))
    if not text:
        return 0.0
    # Only dollar-scale figures: ignore item numbers, percentages, dates, counts.
    memo_amounts = {n for n in _numbers(text) if n >= 1000}
    if not memo_amounts:
        return 0.0
    allowed = _allowed(workspace)
    grounded = sum(1 for n in memo_amounts if n in allowed)
    return grounded / len(memo_amounts)


rk.amounts_are_grounded(weight=1.0)
