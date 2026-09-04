"""Format: the memo follows the skill's review memo template."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import memo_text  # noqa: E402

SECTIONS = (
    "## contract terms used",
    "## script findings",
    "## findings the script cannot make",
    "## items on hold",
    "## items ready",
    "## documents",
    "## next steps",
    "## sources",
)


@criterion(description="memo opens with a title, status line, and one-line finding")
def header_block(workspace: Path) -> bool:
    text = memo_text(workspace)
    head = text[:1200].lower()
    return head.startswith("# ") and "**status:**" in head and "**in one line:**" in head


@criterion(description="template sections present")
def template_sections(workspace: Path) -> float:
    low = memo_text(workspace).lower()
    return sum(1 for s in SECTIONS if s in low) / len(SECTIONS)


@criterion(description="documents table records present, missing, not required, or open")
def documents_table(workspace: Path) -> bool:
    low = memo_text(workspace).lower()
    start = low.find("## documents")
    if start < 0:
        return False
    section = low[start : start + 6000]
    return "| present" in section or "| missing" in section or "| open" in section


rk.header_block(weight=1.0)
rk.template_sections(weight=2.0)
rk.documents_table(weight=1.0)
