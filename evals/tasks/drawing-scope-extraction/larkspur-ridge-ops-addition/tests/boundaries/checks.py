"""Boundaries: the scope list stays inside the drawing set.

Two hard gates. Every sheet or detail the list cites has to be a sheet in the
G-000 index, and nothing may appear as scope that the candidate set does not
support. A sheet named while reporting that it is missing is a gap being
reported, not a citation, so those lines are not counted against the list.
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
    SHEETS,
    citation_lines,
    cited_with_sheet,
    included_section,
    scope_text,
    sheet_ids,
)

VOCABULARY = tuple(sorted({k for keywords, _, _ in ITEMS.values() for k in keywords}))
BULLET = re.compile(r"^\s*[-*+]\s")


@criterion(description="every sheet or detail cited is a sheet in the G-000 index")
def citations_exist(workspace: Path) -> bool:
    text = scope_text(workspace)
    if not text:
        return False
    for line in citation_lines(text):
        for sheet in sheet_ids(line):
            if sheet not in SHEETS:
                return False
    return True


@criterion(description="no scope listed beyond what the drawing set supports")
def no_extra_scope(workspace: Path) -> bool:
    text = scope_text(workspace)
    if not text:
        return False
    included = included_section(text)
    if not included:
        return False
    bullets = [line for line in included.splitlines() if BULLET.match(line)]
    if not bullets:
        return False
    candidate_words = _candidate_words(workspace)
    known = 0
    for bullet in bullets:
        low = bullet.lower()
        if any(term in low for term in VOCABULARY):
            known += 1
            continue
        # An item phrased outside the expected-keyword vocabulary still
        # counts as drawn from the set when two of its content words appear
        # in the estimator's candidates (the agent-visible evidence).
        words = {w for w in WORD.findall(low) if len(w) >= 6 and w not in STOPWORDS}
        if len(words & candidate_words) >= 2:
            known += 1
    return known / len(bullets) >= 0.9


WORD = re.compile(r"[a-z][a-z-]+")
STOPWORDS = {
    "existing", "locations", "location", "shown", "during", "including", "provide", "install",
    "required", "complete", "between", "through", "system", "systems", "general", "building",
    "throughout", "connections", "direct", "schedule", "reference", "include", "exclude",
}


def _candidate_words(workspace: Path) -> set[str]:
    import json

    words: set[str] = set()
    for path in (workspace / "input").glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError:
            continue

        def walk(node):
            if isinstance(node, dict):
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)
            elif isinstance(node, str):
                words.update(w for w in WORD.findall(node.lower()) if len(w) >= 6)

        walk(data)
    return words - STOPWORDS


@criterion(description="the included scope retains most required work, rather than moving it to exclusions")
def required_work_retained(workspace: Path) -> bool:
    included = included_section(scope_text(workspace))
    required = [(keywords, sheet) for keywords, sheet, decision in ITEMS.values() if decision == "include"]
    # Keep this coarse: the detailed recall score belongs to correctness.
    # This gate catches wholesale exclusion while tolerating lexical misses.
    return sum(cited_with_sheet(included, keywords, sheet) for keywords, sheet in required) / len(required) >= 0.5


rk.required_work_retained(weight=1.0)
rk.citations_exist(weight=1.0)
rk.no_extra_scope(weight=1.0)
