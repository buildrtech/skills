"""Format: the RFI follows the skill's references/rfi-template.md."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import has_phrase, rfi_text, table_rows  # noqa: E402

HEADER_FIELDS = (
    "project",
    "from",
    "to",
    "cc",
    "date issued",
    "response needed by",
    "location",
    "discipline",
)

SECTIONS = (
    "## question",
    "## references",
    "## suggested resolution",
    "## impact",
    "## attachments",
)

LOG_COLUMNS = ("number", "subject", "ball in court", "status", "cost impact", "schedule impact")


def _title(text: str) -> str:
    text = text.lstrip()
    return text.splitlines()[0] if text else ""


@criterion(description="title line is '# RFI-<number>: <subject>'")
def title_line(workspace: Path) -> bool:
    return re.match(r"^# RFI-\S+:\s+\S", _title(rfi_text(workspace))) is not None


@criterion(description="subject is under twelve words and is not a conclusion")
def subject_short(workspace: Path) -> bool:
    title = _title(rfi_text(workspace))
    if ":" not in title:
        return False
    subject = title.split(":", 1)[1].strip()
    return 0 < len(subject.split()) <= 12


@criterion(description="header table carries the template fields")
def header_fields(workspace: Path) -> float:
    rows = table_rows(rfi_text(workspace)[:4000])
    labels = {r[0].strip().lower() for r in rows if r}
    return sum(1 for f in HEADER_FIELDS if f in labels) / len(HEADER_FIELDS)


@criterion(description="template sections present")
def template_sections(workspace: Path) -> float:
    low = rfi_text(workspace).lower()
    return sum(1 for s in SECTIONS if s in low) / len(SECTIONS)


@criterion(description="log row table uses the template columns")
def log_columns(workspace: Path) -> float:
    rows = table_rows(rfi_text(workspace))
    best = 0.0
    for r in rows:
        labels = {c.lower() for c in r}
        best = max(best, sum(1 for c in LOG_COLUMNS if c in labels) / len(LOG_COLUMNS))
    return best


@criterion(description="closes with a note on what was verified and what was not")
def verification_note(workspace: Path) -> bool:
    return has_phrase(rfi_text(workspace), "verified", "verify", "confirmed against", "checked against")


rk.title_line(weight=1.0)
rk.subject_short(weight=1.0)
rk.header_fields(weight=2.0)
rk.template_sections(weight=2.0)
rk.log_columns(weight=1.0)
rk.verification_note(weight=1.0)
