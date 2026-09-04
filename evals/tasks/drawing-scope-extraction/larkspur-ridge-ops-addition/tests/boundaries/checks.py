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
    known = 0
    for bullet in bullets:
        low = bullet.lower()
        if any(term in low for term in VOCABULARY):
            known += 1
    return known / len(bullets) >= 0.9


rk.citations_exist(weight=1.0)
rk.no_extra_scope(weight=1.0)
