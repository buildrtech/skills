"""Correctness: did the memo find what was planted, and did it lead with hold?

Truth comes from tests/fixtures/script-output.md (the checker run on the
hidden fixture) and the planted problems listed in Task.md. Nothing here
trusts the memo's own claims about what it checked.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import has_all, has_amount, has_phrase, memo_text  # noqa: E402

# Each planted script-detectable finding, expressed as the amounts a correct
# memo must state together. Wording is free; amounts are not.
PLANTED = {
    "line04_continuity": ("46500", "43000", "3500"),
    "line06_percent": ("72000", "40.00"),
    "line07_over_100": ("54000", "52000"),
    "line11_stored_retainage": ("13475", "3600"),
    "line12_missing": ("11800",),
    "line13_balance": ("301500", "311500"),
    "co002_line2": ("24750", "16550"),
    "co002_line3": ("3204750", "3196550"),
    "sov_total_short": ("3086750", "109800"),
    "line5_retainage": ("150240", "153840"),
    "line8_due_math": ("564965", "565965"),
}

# Findings the script cannot make; these need the document list and the
# cover letter. Each is a (phrase group, amount group) pair.
MANUAL = {
    "co002_named": (("CO-002",), ("8200",)),
    "fire_protection_removed": (("fire protection",), ("11800",)),
    "line08_double_count": (("overhead door",), ("15000",)),
    "line11_offsite_no_insurance": (("joliet", "off-site", "off site", "yard"), ("36000",)),
    "payroll_aug21_missing": (("august 21", "aug 21", "8/21", "aug. 21"), ()),
    "waivers_missing": (("kestrel", "tallgrass", "meridian"), ()),
    "milestone_not_reached": (("48.1", "not reached", "milestone"), ()),
}


@criterion(description="memo exists at output/review-memo.md and is not trivial")
def memo_exists(workspace: Path) -> bool:
    return len(memo_text(workspace)) > 2000


@criterion(description="status line recommends hold for review")
def status_is_hold(workspace: Path) -> bool:
    text = memo_text(workspace)
    return has_phrase(text, "recommend hold for review")


@criterion(description="planted script-detectable findings stated with their amounts")
def planted_findings(workspace: Path) -> float:
    text = memo_text(workspace)
    if not text:
        return 0.0
    hits = sum(1 for amounts in PLANTED.values() if has_all(text, *amounts))
    return hits / len(PLANTED)


@criterion(description="findings the script cannot make: change order, documents, storage, payroll")
def manual_findings(workspace: Path) -> float:
    text = memo_text(workspace)
    if not text:
        return 0.0
    hits = 0
    for phrases, amounts in MANUAL.values():
        if has_phrase(text, *phrases) and (not amounts or has_all(text, *amounts)):
            hits += 1
    return hits / len(MANUAL)


@criterion(description="script findings table pasted unchanged: counts and recomputed Line 8")
def script_output_present(workspace: Path) -> bool:
    text = memo_text(workspace)
    return has_phrase(text, "11 error, 7 warning") and has_amount(text, "562365")


@criterion(description="hold list has at least six rows")
def hold_list_rows(workspace: Path) -> bool:
    text = memo_text(workspace)
    low = text.lower()
    start = low.find("## items on hold")
    if start < 0:
        return False
    end = low.find("\n## ", start + 5)
    section = text[start : end if end > 0 else len(text)]
    rows = [ln for ln in section.splitlines() if ln.startswith("|") and not ln.startswith("|---") and not ln.lower().startswith("| #")]
    return len(rows) >= 6


rk.memo_exists(weight=1.0)
rk.status_is_hold(weight=2.0)
rk.planted_findings(weight=4.0)
rk.manual_findings(weight=2.0)
rk.script_output_present(weight=1.0)
rk.hold_list_rows(weight=1.0)
