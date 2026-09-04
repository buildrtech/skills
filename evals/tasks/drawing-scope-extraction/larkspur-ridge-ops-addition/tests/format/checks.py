"""Format: the scope list follows the shape the skill's script prints."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import INCLUDED_DIVISIONS, has_phrase, ledger_section, scope_text  # noqa: E402

SECTIONS = (
    ("## included scope", "## scope"),
    ("## assumptions",),
    ("## exclusions",),
    ("## rfis",),
    ("## coverage ledger", "## coverage"),
)


@criterion(description="opens with a title naming the scope list and the set")
def title_and_summary(workspace: Path) -> bool:
    text = scope_text(workspace)
    head = text[:300].lower()
    return text.startswith("# ") and "scope list" in head


@criterion(description="scope grouped under a heading per CSI division")
def grouped_by_division(workspace: Path) -> float:
    low = scope_text(workspace).lower()
    if not low:
        return 0.0
    return sum(1 for d in INCLUDED_DIVISIONS if f"division {d}" in low) / len(INCLUDED_DIVISIONS)


@criterion(description="included scope, assumptions, exclusions, RFIs, and coverage ledger sections present")
def standard_sections(workspace: Path) -> float:
    text = scope_text(workspace)
    if not text:
        return 0.0
    return sum(1 for group in SECTIONS if has_phrase(text, *group)) / len(SECTIONS)


@criterion(description="coverage ledger is a sheet-by-sheet table")
def ledger_table(workspace: Path) -> bool:
    text = scope_text(workspace)
    ledger = ledger_section(text)
    if not ledger:
        return False
    return has_phrase(ledger, "| sheet ", "### sheets", "| sheet |")


rk.title_and_summary(weight=1.0)
rk.grouped_by_division(weight=2.0)
rk.standard_sections(weight=2.0)
rk.ledger_table(weight=1.0)
