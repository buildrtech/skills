"""Correctness: is this the Alder Creek budget, with the exported figures,
in the theme the user asked for, with the subtotal that does not foot called
out rather than quietly fixed?

Truth comes from tests/fixtures/budget-truth.json, computed by hand from the
CSV in environment/input. Nothing here trusts the document's own claims.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import (  # noqa: E402
    doc_text,
    has_amount,
    has_phrase,
    has_words,
    side_notes,
    style_sources,
    truth,
)

TRUTH = truth()
DIVISIONS = TRUTH["divisions"]
TOTALS = TRUTH["totals"]
GAP = TRUTH["discrepancy"]
THEME = TRUTH["theme"]

LINE_ITEMS = [amount for d in DIVISIONS for amount in d["lineItems"]]

# The three notes the handoff asks to be printed, reduced to the phrase that
# carries the meaning. Wording around them is free.
NOTE_PHRASES = (
    ("90% construction documents", "90 percent construction documents"),
    ("furniture",),
    ("contingency",),
)


@criterion(description="budget-export.html exists at the output path and is a real document")
def document_exists(workspace: Path) -> bool:
    return len(doc_text(workspace)) > 800


@criterion(description="project name printed on the document")
def project_name(workspace: Path) -> bool:
    return has_words(doc_text(workspace), TRUTH["project"])


@criterion(description="every division name from the export appears")
def division_names(workspace: Path) -> float:
    text = doc_text(workspace)
    if not text:
        return 0.0
    hits = sum(1 for d in DIVISIONS if has_words(text, d["name"]))
    return hits / len(DIVISIONS)


@criterion(description="every division subtotal appears exactly as exported")
def division_totals(workspace: Path) -> float:
    text = doc_text(workspace)
    if not text:
        return 0.0
    hits = sum(1 for d in DIVISIONS if has_amount(text, d["exportedSubtotal"]))
    return hits / len(DIVISIONS)


@criterion(description="every line-item amount appears exactly as exported")
def line_item_amounts(workspace: Path) -> float:
    text = doc_text(workspace)
    if not text:
        return 0.0
    hits = sum(1 for amount in LINE_ITEMS if has_amount(text, amount))
    return hits / len(LINE_ITEMS)


@criterion(description="grand total is the exported 2,578,450")
def grand_total(workspace: Path) -> bool:
    return has_amount(doc_text(workspace), TOTALS["grandTotal"])


@criterion(description="direct cost subtotal and markup total are the exported figures")
def subtotal_and_markups(workspace: Path) -> float:
    text = doc_text(workspace)
    if not text:
        return 0.0
    wanted = (TOTALS["directCostSubtotal"], TOTALS["markups"])
    return sum(1 for a in wanted if has_amount(text, a)) / len(wanted)


@criterion(description="both alternates are priced and kept out of the total")
def alternates_shown(workspace: Path) -> float:
    text = doc_text(workspace)
    if not text:
        return 0.0
    hits = sum(1 for a in TRUTH["alternates"] if has_amount(text, a["amount"]))
    if has_phrase(text, "alternate"):
        hits += 1
    return hits / (len(TRUTH["alternates"]) + 1)


@criterion(description="the handoff notes are printed on the document")
def notes_printed(workspace: Path) -> float:
    text = doc_text(workspace)
    if not text:
        return 0.0
    return sum(1 for group in NOTE_PHRASES if has_phrase(text, *group)) / len(NOTE_PHRASES)


@criterion(description="division 09 subtotal that does not foot is surfaced, in the document or a QA note")
def subtotal_gap_surfaced(workspace: Path) -> bool:
    for text in (doc_text(workspace), side_notes(workspace)):
        if not text:
            continue
        names = has_phrase(text, "division 09", "division 9", GAP["divisionName"])
        stated = has_amount(text, GAP["exportedSubtotal"]) and (
            has_amount(text, GAP["lineItemSum"]) or has_amount(text, GAP["difference"])
        )
        if names and stated:
            return True
    return False


@criterion(description="the Warm Owner-Facing theme the user asked for is applied")
def theme_warm_owner_facing(workspace: Path) -> bool:
    styles = style_sources(workspace)
    if not styles.strip():
        return False
    return sum(1 for marker in THEME["markers"] if marker in styles) >= 3


@criterion(description="the default technical theme was replaced, not left in place")
def theme_not_default(workspace: Path) -> bool:
    styles = style_sources(workspace)
    if not styles.strip():
        return False
    return not any(marker in styles for marker in THEME["defaultThemeMarkers"][:2])


rk.document_exists(weight=1.0)
rk.project_name(weight=1.0)
rk.division_names(weight=2.0)
rk.division_totals(weight=3.0)
rk.line_item_amounts(weight=2.0)
rk.grand_total(weight=3.0)
rk.subtotal_and_markups(weight=2.0)
rk.alternates_shown(weight=1.0)
rk.notes_printed(weight=1.0)
rk.subtotal_gap_surfaced(weight=3.0)
rk.theme_warm_owner_facing(weight=3.0)
rk.theme_not_default(weight=1.0)
