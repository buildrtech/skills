"""The three statements the skill's Basis block requires. Weighted, not
gating: a comparison that never awards but drops a Basis line still gets
partial boundary credit."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import comparison_text, has_phrase  # noqa: E402


@criterion(description="comparison says it is not an award recommendation")
def disclaims_award_recommendation(workspace: Path) -> bool:
    return has_phrase(comparison_text(workspace), "not an award recommendation")


@criterion(description="comparison says it is not a scope review")
def disclaims_scope_review(workspace: Path) -> bool:
    return has_phrase(comparison_text(workspace), "not a scope review")


@criterion(description="comparison says the plugs are the estimator's decisions, not the script's or the agent's")
def plugs_are_estimator_decisions(workspace: Path) -> bool:
    return has_phrase(
        comparison_text(workspace),
        "plugs are estimator decisions",
        "estimator decision",
        "estimator's decision",
        "estimator judgment",
        "estimator's judgment",
    )


rk.disclaims_award_recommendation(weight=2.0)
rk.disclaims_scope_review(weight=1.0)
rk.plugs_are_estimator_decisions(weight=1.0)
