"""Correctness: did the review state every planted date, requirement, and risk,
with its value and a citation to the section it came from?

Truth comes from tests/fixtures/planted-facts.json, which was written from the
synthetic IFB and Addendum 1 before the reference review existed. Nothing here
trusts the review's own claims about what it read.

Each planted fact is matched against one logical line of the review: the line
must mention the fact (a keyword), state its value (the date, percentage, or
dollar amount), and cite the IFB section or the addendum it came from.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import (  # noqa: E402
    cites_section,
    logical_lines,
    fixture,
    has_amount,
    has_date,
    has_percent,
    has_phrase,
    keyword_lines,
    memo_text,
    section_body,
    table_rows,
)


def _line_states(line: str, spec: dict) -> bool:
    """True when this line carries the fact's value and its citation."""
    if "date" in spec:
        y, m, d = (int(x) for x in spec["date"].split("-"))
        if not has_date(line, (y, m, d)):
            return False
    if "percent" in spec and not has_percent(line, spec["percent"]):
        return False
    amounts = ([spec["amount"]] if "amount" in spec else []) + list(spec.get("amounts", []))
    if not all(has_amount(line, a) for a in amounts):
        return False
    if "any" in spec and not has_phrase(line, *spec["any"]):
        return False
    section = spec.get("section")
    if section and not any(cites_section(line, s) for s in section.split("|")):
        return False
    return True


def _stated(text: str, spec: dict) -> bool:
    """A fact is stated when one logical line carries its keyword and value,
    and the citation is on that line or within the four logical lines above
    it (a block heading such as "**Insurance** (IFB §8):" cites for its
    bullets)."""
    lines = logical_lines(text)
    keywords = tuple(k.lower() for k in spec["keywords"])
    value_spec = {k: v for k, v in spec.items() if k != "section"}
    section = spec.get("section")
    for i, ln in enumerate(lines):
        low = ln.lower()
        if not any(k in low for k in keywords):
            continue
        if not _line_states(ln, value_spec):
            continue
        if not section:
            return True
        window = " ".join(lines[max(0, i - 4) : i + 1])
        if any(cites_section(window, s) for s in section.split("|")):
            return True
    return False


def _share(workspace: Path, group: str) -> float:
    text = memo_text(workspace)
    if not text:
        return 0.0
    specs = fixture()[group]
    hits = sum(1 for spec in specs.values() if _stated(text, spec))
    return hits / len(specs)


@criterion(description="review exists at output/intake-review.md and is not trivial")
def review_exists(workspace: Path) -> bool:
    return len(memo_text(workspace)) > 2000


@criterion(description="each planted key date stated with its date and a citation")
def key_dates(workspace: Path) -> float:
    return _share(workspace, "dates")


@criterion(description="each planted bid requirement stated with its value and a citation")
def requirements_stated(workspace: Path) -> float:
    return _share(workspace, "requirements")


@criterion(description="each planted risk flagged with its value and a citation")
def risks_flagged(workspace: Path) -> float:
    return _share(workspace, "risks")


@criterion(description="notes that Addendum 1 moved the bid date off October 13")
def addendum_change_noted(workspace: Path) -> bool:
    text = memo_text(workspace)
    if not text:
        return False
    return _stated(text, fixture()["addendum_change"])


@criterion(description="go/no-go scorecard present with a rating per criterion")
def scorecard_present(workspace: Path) -> bool:
    text = memo_text(workspace)
    body = section_body(text, "go/no-go scorecard") or section_body(text, "scorecard")
    if not body:
        return False
    rows = [r for r in table_rows(body) if r.count("|") >= 3]
    return len(rows) >= 6


@criterion(description="a bid/no-bid recommendation is given, with a value")
def recommendation_present(workspace: Path) -> bool:
    text = memo_text(workspace)
    # The template label is "Recommendation"; accept equivalent labels an
    # agent may use for the same go/no-go call.
    for ln in keyword_lines(text, ("recommendation", "recommend", "decision posture", "bid posture", "verdict", "go/no-go call")):
        if has_phrase(ln, "go with conditions", "no-go", "no go", "no-bid", "no bid", "go"):
            return True
    return False


@criterion(description="the recommendation is framed as a recommendation for the user to decide")
def decision_left_to_user(workspace: Path) -> bool:
    return has_phrase(
        memo_text(workspace),
        "not a decision",
        "recommendation, not",
        "call is yours",
        "decision is yours",
        "decision stays with you",
        "decision remains with you",
        "yours to make",
        "for you to make",
        "you make the call",
        "you will make the call",
        "your decision",
        "the team decides",
        "for the precon meeting to decide",
    )


rk.review_exists(weight=1.0)
rk.key_dates(weight=3.0)
rk.requirements_stated(weight=3.0)
rk.risks_flagged(weight=3.0)
rk.addendum_change_noted(weight=1.0)
rk.scorecard_present(weight=1.0)
rk.recommendation_present(weight=1.0)
rk.decision_left_to_user(weight=1.0)
