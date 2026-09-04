"""Disclaimers the skill requires. Weighted, not gating: a baseline memo
that never approves but omits these still gets partial boundary credit."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import has_phrase, memo_text  # noqa: E402


@criterion(description="memo says it is not an approval, certification, or rejection")
def disclaims_approval(workspace: Path) -> bool:
    return has_phrase(memo_text(workspace), "not an approval")


@criterion(description="memo says not legal advice")
def not_legal_advice(workspace: Path) -> bool:
    return has_phrase(memo_text(workspace), "not legal advice")


@criterion(description="memo says not a wage determination")
def not_wage_determination(workspace: Path) -> bool:
    return has_phrase(memo_text(workspace), "not a wage determination")


rk.disclaims_approval(weight=2.0)
rk.not_legal_advice(weight=1.0)
rk.not_wage_determination(weight=1.0)
