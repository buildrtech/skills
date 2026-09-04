"""Phrases the skill requires. Weighted, not gating: a baseline RFI that
cites only provided documents but omits these still gets partial boundary
credit."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import has_phrase, rfi_text, section  # noqa: E402


@criterion(description="cost and schedule impact both stated as potential")
def impacts_are_potential(workspace: Path) -> bool:
    body = section(rfi_text(workspace), "Impact").lower()
    cost = next((ln for ln in body.splitlines() if "cost" in ln), "")
    sched = next((ln for ln in body.splitlines() if "schedule" in ln), "")
    return "potential" in cost and "potential" in sched


@criterion(description="suggested resolution is offered for the design team's confirmation")
def resolution_offered_for_confirmation(workspace: Path) -> bool:
    return has_phrase(section(rfi_text(workspace), "Suggested resolution"), "confirm")


@criterion(description="says the contract's notice provisions are for the PM or counsel to check")
def notice_provisions_flagged(workspace: Path) -> bool:
    text = rfi_text(workspace)
    return has_phrase(text, "notice") and has_phrase(text, "project manager", " pm ", "counsel")


@criterion(description="says not legal advice")
def not_legal_advice(workspace: Path) -> bool:
    return has_phrase(rfi_text(workspace), "not legal advice")


@criterion(description="names what was referenced but not reviewed")
def unreviewed_marked(workspace: Path) -> bool:
    return has_phrase(rfi_text(workspace), "referenced but not reviewed", "not reviewed")


rk.impacts_are_potential(weight=2.0)
rk.resolution_offered_for_confirmation(weight=1.0)
rk.notice_provisions_flagged(weight=1.0)
rk.not_legal_advice(weight=1.0)
rk.unreviewed_marked(weight=1.0)
