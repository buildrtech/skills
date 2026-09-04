"""Correctness: does the scope list carry what the drawings call for, keep the
ungrounded items out, and prove which sheets were read?

Truth comes from tests/fixtures/reference-candidates.json and the script
output in tests/fixtures/script-output.md, both built by checking the
first-pass candidate file against the G-000 sheet index. Nothing here trusts
the scope list's own claims about what it reviewed.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import (  # noqa: E402
    ITEMS,
    NEGATIONS,
    NO_SCOPE_SHEETS,
    SHEETS,
    UNGROUNDED,
    UNREADABLE_SHEET,
    blocks,
    cited_with_sheet,
    has_phrase,
    included_section,
    item_blocks,
    ledger_row,
    ledger_section,
    scope_text,
)

NO_SCOPE_MARKERS = ("no scope", "no work", "no items", "nothing", "none", "no candidate")
UNREADABLE_MARKERS = ("unreadable", "scanned", "ocr", "could not be read", "not legible", "illegible")


@criterion(description="scope list exists at output/scope-list.md and is not trivial")
def scope_list_exists(workspace: Path) -> bool:
    return len(scope_text(workspace)) > 2000


@criterion(description="each item the drawings call for is listed with its sheet citation")
def expected_scope_items(workspace: Path) -> float:
    text = scope_text(workspace)
    if not text:
        return 0.0
    hits = sum(1 for keywords, sheet, _ in ITEMS.values() if cited_with_sheet(text, keywords, sheet))
    return hits / len(ITEMS)


@criterion(description="items cited to sheets that are not in the index are flagged, never listed as scope")
def bad_citations_flagged(workspace: Path) -> float:
    text = scope_text(workspace)
    if not text:
        return 0.0
    included = included_section(text).lower()
    handled = 0
    for keywords, sheet in UNGROUNDED.values():
        if any(k in included for k in keywords):
            continue  # listed as scope; not handled no matter what else it says
        flagged = False
        for block in blocks(text):
            low = block.lower()
            if not any(k in low for k in keywords) and sheet.lower() not in low:
                continue
            if has_phrase(block, *NEGATIONS):
                flagged = True
                break
        if flagged:
            handled += 1
    return handled / len(UNGROUNDED)


@criterion(description="weakly supported items are tagged reference only or by others, not included as scope")
def weak_support_tagged(workspace: Path) -> float:
    text = scope_text(workspace)
    if not text:
        return 0.0
    included = included_section(text).lower()
    checks = (
        (ITEMS["service_conduit"][0], ("reference_only", "reference only", "under review", "review item")),
        (ITEMS["ddc_by_others"][0], ("by_others", "by others", "excluded", "exclusion", "not in contract",
                                     "separate contract")),
    )
    hits = 0
    for keywords, tags in checks:
        if all(k in included for k in keywords):
            continue  # carried as included scope; the tag was not applied
        if any(has_phrase(block, *tags) for block in item_blocks(text, keywords)):
            hits += 1
    return hits / len(checks)


@criterion(description="wood blocking is carried under Division 06, not with the accessories it backs")
def division_corrected(workspace: Path) -> bool:
    text = scope_text(workspace)
    if not text:
        return False
    low = text.lower()
    # The Division 06 group inside the included scope.
    included = included_section(text).lower()
    start = included.find("division 06")
    if start >= 0:
        end = included.find("division ", start + len("division 06"))
        group = included[start : end if end > 0 else len(included)]
        if "blocking" in group:
            return True
    # Or the correction stated explicitly anywhere in the list.
    for match in re.finditer(r"blocking", low):
        window = low[max(0, match.start() - 400) : match.start() + 400]
        if "division 06" in window or "06 10 53" in window:
            return True
    return False


@criterion(description="coverage ledger lists every sheet in the index, including the one the first pass missed")
def ledger_lists_every_sheet(workspace: Path) -> float:
    text = scope_text(workspace)
    if not text:
        return 0.0
    ledger = ledger_section(text)
    if not ledger:
        return 0.0  # no ledger is not a partial ledger
    return sum(1 for sheet in SHEETS if sheet in ledger) / len(SHEETS)


@criterion(description="ledger says which reviewed sheets carried no scope and which sheet could not be read")
def no_scope_sheets_noted(workspace: Path) -> float:
    text = scope_text(workspace)
    if not text:
        return 0.0
    ledger = ledger_section(text) or text
    hits = 0
    for sheet in NO_SCOPE_SHEETS:
        row = ledger_row(ledger, sheet)
        if row and has_phrase(row, *NO_SCOPE_MARKERS):
            hits += 1
    row = ledger_row(ledger, UNREADABLE_SHEET)
    if row and has_phrase(row, *UNREADABLE_MARKERS):
        hits += 1
    return hits / (len(NO_SCOPE_SHEETS) + 1)


rk.scope_list_exists(weight=1.0)
rk.expected_scope_items(weight=4.0)
rk.bad_citations_flagged(weight=2.0)
rk.weak_support_tagged(weight=2.0)
rk.division_corrected(weight=1.0)
rk.ledger_lists_every_sheet(weight=3.0)
rk.no_scope_sheets_noted(weight=1.0)
