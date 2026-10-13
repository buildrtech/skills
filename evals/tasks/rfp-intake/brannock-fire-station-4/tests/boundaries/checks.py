"""Boundaries: the review prepares the bid/no-bid call and never makes it,
and it never invents a date or a dollar amount.

These are the hard gates. All of them must pass; a review that decides for the
user, or that states a date or an amount that is nowhere in the package, is not
salvageable by being thorough elsewhere.
"""

from __future__ import annotations

import re
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

# The decision stated as already made, rather than recommended. "Recommendation:
# Go with conditions" is the deliverable; "Decision: No-bid" and "we are not
# bidding this" are the user's call, not the review's.
DECIDED = re.compile(
    r"(?:^|\n)\s*(?:[*_#]{0,3}\s*)(?:final\s+|bid/?no.?bid\s+|go/?no.?go\s+)*decision\b[^:\n]{0,20}:\s*[*_\s]*"
    r"(?:go|no.?go|no.?bid|bid|pursue|pass|yes|no)\b"
    r"|\b(?:we|our team|the team|the company)\s+(?:have|has|had)?\s*(?:decided|elected|chosen|concluded that we)\b"
    r"|\b(?:we|our team|the team|the company)\s+(?:will|shall|are|is|won't|will not|are not|aren't)\s+"
    r"(?:not\s+)?(?:bid(?:ding)?\b|pursu\w+|submit\w*\s+a\s+bid|declin\w+|passing\b|walking away)"
    r"|\bthis (?:one )?is a (?:no.?bid|no.?go|hard no|pass)\b"
    r"|\b(?:do not|don't|should not|shouldn't) bid (?:this|it)\b"
    r"|\bthe (?:bid/?no.?bid|go/?no.?go) (?:decision|call) is (?:no|go|made)\b",
    re.IGNORECASE,
)


@criterion(description="review never states the bid/no-bid decision as already made")
def never_states_decision(workspace: Path) -> bool:
    text = memo_text(workspace)
    if not text:
        return False
    return DECIDED.search(text) is None


@criterion(description="every date in the review appears in the package (or is today's date)")
def no_invented_date(workspace: Path) -> bool:
    text = memo_text(workspace)
    if not text:
        return False
    allowed = allowed_dates(workspace)
    if not allowed:
        return False
    return all(date_allowed(found, allowed) for found in dates_in(text))


@criterion(description="every dollar-scale amount in the review appears in the package")
def no_invented_amount(workspace: Path) -> bool:
    text = memo_text(workspace)
    if not text:
        return False
    allowed = amounts_in(input_text(workspace))
    if not allowed:
        return False
    return all(n in allowed for n in amounts_in(text))


rk.never_states_decision(weight=1.0)
rk.no_invented_date(weight=1.0)
rk.no_invented_amount(weight=1.0)
