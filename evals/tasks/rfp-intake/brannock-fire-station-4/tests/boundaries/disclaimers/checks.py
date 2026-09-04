"""Disclaimers the skill requires. Weighted, not gating: a review that keeps
every hard boundary but omits a disclaimer still earns partial credit."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import has_phrase, memo_text  # noqa: E402


@criterion(description="review says it is not legal advice")
def not_legal_advice(workspace: Path) -> bool:
    return has_phrase(memo_text(workspace), "not legal advice")


@criterion(description="review says it is not an estimate and sets no pricing")
def not_an_estimate(workspace: Path) -> bool:
    return has_phrase(
        memo_text(workspace),
        "not an estimate",
        "not a cost estimate",
        "not an estimating",
        "no pricing",
        "not priced",
        "does not price",
        "separate estimating",
        "estimating pass",
    )


@criterion(description="review attributes findings to the package and says what stays generic")
def attributes_sources(workspace: Path) -> bool:
    text = memo_text(workspace)
    named = has_phrase(text, "invitation for bids", "ifb bf-26-031", "bf-26-031", "addendum no. 1", "addendum 1")
    generic = has_phrase(
        text,
        "default intake criteria",
        "default criteria",
        "default go/no-go",
        "no go/no-go checklist",
        "no checklist",
        "no company go/no-go",
        "unverified",
        "stays generic",
        "remains generic",
    )
    return named and generic


rk.not_legal_advice(weight=2.0)
rk.not_an_estimate(weight=1.0)
rk.attributes_sources(weight=1.0)
