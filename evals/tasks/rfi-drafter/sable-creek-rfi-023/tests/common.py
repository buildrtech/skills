"""Shared helpers for the sable-creek-rfi-023 verifier.

Everything here reads the agent's RFI and the hidden fixture. Nothing here
is copied into the agent image.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

RFI = "output/rfi-023.md"
TRUTH = Path(__file__).resolve().parent / "fixtures" / "truth.json"

INPUT_FILES = (
    "request.md",
    "drawing-excerpts.md",
    "spec-03-30-00.md",
    "submittal-03-30-00-02.md",
)

# Reference tokens the RFI may cite. Sheet ids like S-001; detail callouts
# like 3/S-101; spec sections like 03 30 00; spec paragraphs like 2.6.C.
SHEET = re.compile(r"\b[A-Z]{1,2}-\d{3}[A-Z]?\b")
DETAIL = re.compile(r"\b\d{1,2}/[A-Z]{1,2}-\d{3}\b")
SPEC = re.compile(r"\b\d{2} \d{2} \d{2}\b")
PARA = re.compile(r"\b\d\.\d{1,2}\.[A-Z]\b")
PSI = re.compile(r"\b(\d{1,2},?\d{3})(?:\s*|-)psi\b", re.IGNORECASE)

MONTHS = {
    m: i + 1
    for i, m in enumerate(
        ("january", "february", "march", "april", "may", "june", "july",
         "august", "september", "october", "november", "december")
    )
}
MONTHS.update({m[:3]: n for m, n in list(MONTHS.items())})
MONTHS["sept"] = 9
DATE_WORDS = re.compile(
    r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b",
    re.IGNORECASE,
)
DATE_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
DATE_SLASH = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")


def rfi_text(workspace: Path) -> str:
    path = workspace / RFI
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def input_text(workspace: Path) -> str:
    parts = []
    for name in INPUT_FILES:
        p = workspace / "input" / name
        if p.is_file():
            parts.append(p.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def truth() -> dict:
    return json.loads(TRUTH.read_text(encoding="utf-8"))


def has_phrase(text: str, *phrases: str) -> bool:
    low = text.lower()
    return any(p.lower() in low for p in phrases)


def section(text: str, heading: str) -> str:
    """Body of the first '## <heading>' section (case-insensitive) up to the next heading."""
    low = text.lower()
    aliases = {
        "question": ("question", "clarification requested"),
        "suggested resolution": ("suggested resolution", "proposed resolution"),
    }
    names = aliases.get(heading.lower(), (heading.lower(),))
    pattern = "(?:" + "|".join(re.escape(name) for name in names) + ")"
    m = re.search(r"^#{1,3}\s+" + pattern + r"\b.*$", low, re.MULTILINE)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^#{1,3}\s+", low[start:], re.MULTILINE)
    end = start + nxt.start() if nxt else len(text)
    return text[start:end]


def dates(text: str) -> set[str]:
    # Quoted source excerpts can wrap dates across Markdown blockquote lines.
    text = re.sub(r"(?m)^\s*>[ \t]?", "", text)
    out: set[str] = set()
    for m in DATE_WORDS.finditer(text):
        mon = MONTHS.get(m.group(1).lower())
        if mon:
            out.add(f"{int(m.group(3)):04d}-{mon:02d}-{int(m.group(2)):02d}")
    for m in DATE_ISO.finditer(text):
        out.add(f"{m.group(1)}-{m.group(2)}-{m.group(3)}")
    for m in DATE_SLASH.finditer(text):
        out.add(f"{int(m.group(3)):04d}-{int(m.group(1)):02d}-{int(m.group(2)):02d}")
    return out


def psi_values(text: str) -> set[str]:
    return {m.group(1).replace(",", "") for m in PSI.finditer(text)}


def has_psi(text: str, value: str) -> bool:
    return value in psi_values(text)


def references(text: str) -> dict[str, set[str]]:
    return {
        "sheets": set(SHEET.findall(text)),
        "details": set(DETAIL.findall(text)),
        "specs": set(SPEC.findall(text)),
        "paragraphs": set(PARA.findall(text)),
    }


def table_rows(text: str) -> list[list[str]]:
    """All markdown table body rows as lists of stripped cells."""
    rows = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s.startswith("|") or re.match(r"^\|\s*-{2,}", s):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        rows.append(cells)
    return rows


def log_rows(text: str, number: str) -> list[list[str]]:
    return [r for r in table_rows(text) if r and r[0].upper() == number.upper()]
