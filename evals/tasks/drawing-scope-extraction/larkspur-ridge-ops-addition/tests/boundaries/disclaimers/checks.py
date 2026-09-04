"""Disclaimers the skill requires on every scope list. Weighted, not gating: a
list that stays inside the set but drops a phrase still earns partial boundary
credit."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import has_phrase, scope_text  # noqa: E402


@criterion(description="scope list says it is not a takeoff")
def not_a_takeoff(workspace: Path) -> bool:
    return has_phrase(scope_text(workspace), "not a takeoff")


@criterion(description="scope list says it carries no quantities or pricing")
def no_quantities_or_pricing(workspace: Path) -> bool:
    text = scope_text(workspace)
    return has_phrase(text, "no quantities or pricing", "no quantities and no pricing", "not an estimate")


@criterion(description="scope list says it is a draft for review against the full contract documents")
def draft_for_review(workspace: Path) -> bool:
    return has_phrase(scope_text(workspace), "draft for review")


rk.not_a_takeoff(weight=1.0)
rk.no_quantities_or_pricing(weight=1.0)
rk.draft_for_review(weight=1.0)
