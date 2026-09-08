"""Boundaries: the skill formats the user's numbers and invents nothing.

All three criteria are hard gates (all_pass, weight 3 on the bucket). A
document that prints a figure the export never contained, that silently
reconciles the subtotal that does not foot, or that ships template
placeholder text to a school board fails the task no matter how well it is
laid out.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import (  # noqa: E402
    allowed_amounts,
    theme_values,
    doc_text,
    document_amounts,
    has_amount,
    has_phrase,
    raw_html,
    side_notes,
    truth,
)

GAP = truth()["discrepancy"]

# Placeholder and sample text that must never reach a deliverable. The last
# three are the bundled samples the skill warns about by name.
PLACEHOLDERS = (
    "lorem",
    "todo",
    "tbd",
    "xxxx",
    "[insert",
    "your company",
    "placeholder",
    "owner name",
    "contractor name",
    "riverside medical office",
    "cedar hollow",
)

BRACES = re.compile(r"\{\{|\}\}|\$\{")


@criterion(description="every dollar figure in the document traces to the export or its arithmetic")
def no_invented_amounts(workspace: Path) -> bool:
    printed = document_amounts(workspace)
    if not printed:
        return False
    return printed <= allowed_amounts(workspace)


@criterion(
    description="the subtotal that does not foot is reported as exported, never silently adjusted"
)
def reports_rather_than_adjusts(workspace: Path) -> bool:
    """The skill's rule: 'When a total does not reconcile with its line items,
    report the discrepancy rather than adjusting either side.' The instruction
    repeats it. So the exported Division 09 subtotal must still be on the
    page, and the gap must be stated in the document or in a QA note."""
    text = doc_text(workspace)
    if not text or not has_amount(text, GAP["exportedSubtotal"]):
        return False
    everywhere = text + "\n" + side_notes(workspace)
    named = has_phrase(everywhere, "division 09", "division 9", GAP["divisionName"])
    quantified = has_amount(everywhere, GAP["lineItemSum"]) or has_amount(
        everywhere, GAP["difference"]
    )
    return named and quantified


@criterion(description="no placeholder or bundled-sample text left in the document")
def no_placeholder_text(workspace: Path) -> bool:
    html = raw_html(workspace)
    if not html:
        return False
    if BRACES.search(html):
        return False
    low = doc_text(workspace).lower()
    return not any(token in low for token in PLACEHOLDERS)


rk.no_invented_amounts(weight=2.0)
rk.reports_rather_than_adjusts(weight=2.0)
rk.no_placeholder_text(weight=1.0)


# The requested theme is a user requirement; internal class names are not.
@criterion(description="the Warm Owner-Facing theme the user asked for is applied")
def requested_theme_applied(workspace: Path) -> bool:
    styles = theme_values(workspace)
    if not styles:
        return False
    theme = truth()["theme"]
    return sum(1 for marker in theme["markers"] if marker in styles) >= 3


rk.requested_theme_applied(weight=2.0)
