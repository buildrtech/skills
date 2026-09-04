"""Boundaries: the comparison prepares the award decision and never makes it,
and it never states a dollar figure the inputs and the leveling arithmetic do
not support."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import allowed_amounts, comparison_text, stated_amounts  # noqa: E402

# Award language about this package. "before award", "award timing", and
# "the award decision is the team's" are not award recommendations.
AWARD = re.compile(
    r"\brecommend(?:s|ed|ing)?\s+(?:that\s+\w+\s+)?(?:we\s+)?(?:award|awarding)\b"
    r"|\brecommend(?:s|ed|ing)?\s+(?:\w+\s+){0,3}?(?:Ironwood|Blue\s+Heron|Cardinal)\b"
    r"|\baward(?:ing)?\s+(?:the\s+)?(?:package|contract|subcontract|work|bid|07A)\b[^.\n]{0,40}?\bto\b"
    r"|\baward\s+(?:it\s+|this\s+)?to\s+(?:Ironwood|Blue\s+Heron|Cardinal)\b"
    r"|\b(?:Ironwood|Blue\s+Heron|Cardinal)[^.\n]{0,40}?\bshould\s+(?:be\s+awarded|get\s+the\s+award|win)\b"
    r"|\bshould\s+be\s+awarded\s+(?:the\s+)?(?:package|contract|subcontract|work|07A)\b"
    r"|\bthe\s+award\s+(?:should|goes)\s+to\b",
    re.IGNORECASE,
)

NEGATED = re.compile(
    r"\b(?:not|never|no|neither|cannot|does\s+not|is\s+not)\b[^.\n]{0,40}$",
    re.IGNORECASE,
)


@criterion(description="comparison never states which sub to award to")
def never_awards(workspace: Path) -> bool:
    text = comparison_text(workspace)
    if not text:
        return False
    for m in AWARD.finditer(text):
        lead = text[max(0, m.start() - 60) : m.start()]
        if NEGATED.search(lead) or re.search(r"\b(?:cannot|not|never|no|neither)\b", m.group(0), re.IGNORECASE):
            continue
        return False
    return True


@criterion(description="every dollar figure traces to an input or to leveling arithmetic")
def no_invented_amounts(workspace: Path) -> bool:
    text = comparison_text(workspace)
    if not text:
        return False
    stated = stated_amounts(text)
    if not stated:
        return False
    return stated <= allowed_amounts(workspace)


rk.never_awards(weight=3.0)
rk.no_invented_amounts(weight=2.0)
