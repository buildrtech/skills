"""Format: the comparison follows the skill's comparison template."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import comparison_text  # noqa: E402

SECTIONS = (
    "## summary",
    "## base scope matrix",
    "## scope gaps and plugs",
    "## adjustments",
    "## alternates",
    "## unit prices",
    "## priced qualifications",
    "## outside package scope",
    "## review items",
    "## qualifications",
    "## evidence",
    "## basis",
)


@criterion(description="opens with the comparison title and the lowest-complete-total headline")
def header_block(workspace: Path) -> bool:
    text = comparison_text(workspace)
    head = text[:1200].lower()
    return head.startswith("# leveled bid comparison") and "**lowest complete leveled total:**" in head


@criterion(description="template sections present")
def template_sections(workspace: Path) -> float:
    low = comparison_text(workspace).lower()
    return sum(1 for s in SECTIONS if s in low) / len(SECTIONS)


@criterion(description="base scope matrix has a column per bidder and a row per base scope")
def matrix_shape(workspace: Path) -> bool:
    text = comparison_text(workspace)
    low = text.lower()
    start = low.find("## base scope matrix")
    if start < 0:
        return False
    end = low.find("\n## ", start + 5)
    section = text[start : end if end > 0 else len(text)]
    header = [ln for ln in section.splitlines() if ln.startswith("|")]
    if not header:
        return False
    first = header[0].lower()
    if not all(name in first for name in ("ironwood", "blue heron", "cardinal")):
        return False
    rows = [ln for ln in header[1:] if not set(ln) <= set("|- :")]
    return len(rows) >= 8


rk.header_block(weight=1.0)
rk.template_sections(weight=2.0)
rk.matrix_shape(weight=1.0)
