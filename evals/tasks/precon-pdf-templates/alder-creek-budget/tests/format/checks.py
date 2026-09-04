"""Format: the document is well-formed HTML with the budget export
template's structure — a titled header, the division table with repeating
column headers, alternates, markups, a totals block, and notes.

Parsing is stdlib html.parser only.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import has_phrase, parse, raw_html, truth, words  # noqa: E402

TRUTH = truth()

SECTIONS = (
    ("division detail", "division summary", "budget detail", "division breakdown"),
    ("alternates", "alternate"),
    ("markups", "markup"),
    ("notes", "note"),
)


@criterion(description="output is parseable HTML with a body and at least one table")
def html_parses(workspace: Path) -> bool:
    html = raw_html(workspace)
    if not html.strip():
        return False
    try:
        doc = parse(workspace)
    except Exception:
        return False
    tags = set(doc.tags)
    return {"html", "body", "table"} <= tags and bool(doc.text.strip())


@criterion(description="header block: project title plus estimate date and preparer")
def header_block(workspace: Path) -> bool:
    doc = parse(workspace)
    titled = any(words(TRUTH["project"]) in words(h) for h in doc.headings)
    return titled and has_phrase(doc.text, "estimate date", "estimate dated") and has_phrase(
        doc.text, TRUTH["preparedBy"]
    )


@criterion(description="template sections present: division detail, alternates, markups, notes")
def template_sections(workspace: Path) -> float:
    doc = parse(workspace)
    haystack = "\n".join(doc.headings) or doc.text
    return sum(1 for group in SECTIONS if has_phrase(haystack, *group)) / len(SECTIONS)


@criterion(description="division table has a repeating header row with the export's columns")
def division_table(workspace: Path) -> bool:
    doc = parse(workspace)
    if "thead" not in doc.tags and "th" not in doc.tags:
        return False
    low = doc.text.lower()
    return all(column in low for column in ("description", "quantity", "total"))


@criterion(description="totals block carries subtotal, markups, and total rows")
def totals_block(workspace: Path) -> bool:
    low = parse(workspace).text.lower()
    return "subtotal" in low and "markup" in low and "total" in low


@criterion(description="page structure kept: print page or page-break rules survive")
def print_ready_page(workspace: Path) -> bool:
    html = raw_html(workspace).lower()
    return any(marker in html for marker in ("pdf-page", "page-break", "@page", "break-inside"))


rk.html_parses(weight=1.0)
rk.header_block(weight=1.0)
rk.template_sections(weight=2.0)
rk.division_table(weight=1.0)
rk.totals_block(weight=1.0)
rk.print_ready_page(weight=1.0)
