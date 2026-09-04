"""Format: the review follows the output template in the skill's
references/intake-checklist.md."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import memo_text, section_body, table_rows  # noqa: E402

SECTIONS = (
    "## key dates",
    "## project snapshot",
    "## requirements to bid",
    "## scope summary",
    "## risk flags",
    "## go/no-go scorecard",
    "## open questions",
    "## sources",
)


@criterion(description="review opens with a title, a recommendation, and a one-line why")
def header_block(workspace: Path) -> bool:
    text = memo_text(workspace)
    head = text[:1200].lower()
    if not head.startswith("# "):
        return False
    import re

    return (
        re.search(r"\*\*recommendation[^*\n]*:\*\*", head) is not None
        and re.search(r"\*\*why(?: in one line)?[^*\n]*:\*\*", head) is not None
    )


@criterion(description="template sections present")
def template_sections(workspace: Path) -> float:
    low = memo_text(workspace).lower()
    return sum(1 for s in SECTIONS if s in low) / len(SECTIONS)


@criterion(description="key dates table has a row per milestone and a source column")
def key_dates_table(workspace: Path) -> bool:
    body = section_body(memo_text(workspace), "key dates")
    if not body:
        return False
    if "source" not in body.lower():
        return False
    rows = [r for r in table_rows(body) if r.count("|") >= 3]
    return len(rows) >= 6


rk.header_block(weight=1.0)
rk.template_sections(weight=2.0)
rk.key_dates_table(weight=1.0)
