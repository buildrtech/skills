"""Shared helpers for the brannock-fire-station-4 verifier.

Everything here reads the agent's review, the agent-visible inputs, and the
hidden fixture. Nothing here is copied into the agent image.
"""

from __future__ import annotations

import json
import re
from decimal import Decimal
from pathlib import Path

MEMO = "output/intake-review.md"
INPUTS = ("invitation-for-bids.md", "addendum-01.md")
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "planted-facts.json"

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}
MONTH_RE = (
    r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
    r"aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
)
DATE = re.compile(
    rf"\b(?P<m1>{MONTH_RE})\.?\s+(?P<d1>\d{{1,2}})(?:st|nd|rd|th)?(?:,?\s+(?P<y1>\d{{4}}))?\b"
    rf"|\b(?P<d2>\d{{1,2}})\s+(?P<m2>{MONTH_RE})\.?,?\s+(?P<y2>\d{{4}})\b"
    r"|\b(?P<y3>\d{4})-(?P<m3>\d{2})-(?P<d3>\d{2})\b"
    r"|\b(?P<m4>\d{1,2})/(?P<d4>\d{1,2})/(?P<y4>\d{4}|\d{2})\b",
    re.IGNORECASE,
)

# Dollar-scale figures: $2,000,000 / 2,000,000.00 / $2M / $2.5 million / 3200.
AMOUNT = re.compile(
    # The trailing guard rejects a partial match of a grouped number ("2" of
    # "2,000") without rejecting a number that is simply followed by a comma
    # ("built in 1968, occupies").
    r"(?<![\d.])\$?\s?(?P<n>\d{1,3}(?:,\d{3})+|\d+)(?:\.(?P<f>\d{1,2}))?\s?(?P<suf>mm|m|million|k)?\b(?!\d|,\d)",
    re.IGNORECASE,
)


def memo_text(workspace: Path) -> str:
    path = workspace / MEMO
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def input_text(workspace: Path) -> str:
    parts = []
    for name in INPUTS:
        p = workspace / "input" / name
        if p.is_file():
            parts.append(p.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def norm(text: str) -> str:
    """Strip currency punctuation so 3,200.00 and $3,200 and 3200 all match."""
    return text.replace("$", "").replace(",", "")


def lines(text: str) -> list[str]:
    return text.splitlines()


def has_phrase(text: str, *phrases: str) -> bool:
    low = text.lower()
    return any(p.lower() in low for p in phrases)


def _month(token: str) -> int | None:
    t = token.lower().rstrip(".")
    if t.isdigit():
        n = int(t)
        return n if 1 <= n <= 12 else None
    return MONTHS.get(t[:4]) or MONTHS.get(t[:3])


def dates_in(text: str) -> list[tuple[int | None, int, int]]:
    """All dates in the text as (year or None, month, day)."""
    out: list[tuple[int | None, int, int]] = []
    for m in DATE.finditer(text):
        g = m.groupdict()
        if g["m1"]:
            # "may 15 percent" is prose, not a date; require a year or a capital M.
            if g["m1"].lower() == "may" and not g["y1"] and g["m1"][0] != "M":
                continue
            month, day, year = _month(g["m1"]), int(g["d1"]), g["y1"]
        elif g["m2"]:
            month, day, year = _month(g["m2"]), int(g["d2"]), g["y2"]
        elif g["m3"]:
            month, day, year = int(g["m3"]), int(g["d3"]), g["y3"]
        else:
            month, day, year = int(g["m4"]), int(g["d4"]), g["y4"]
            if year and len(year) == 2:
                year = "20" + year
        if month is None or not 1 <= month <= 12 or not 1 <= day <= 31:
            continue  # "lines 13-19" is a citation, not a date
        out.append((int(year) if year else None, month, day))
    return out


def has_date(text: str, ymd: tuple[int, int, int]) -> bool:
    y, mo, d = ymd
    return any((yy in (None, y)) and mm == mo and dd == d for yy, mm, dd in dates_in(text))


def date_allowed(found: tuple[int | None, int, int], allowed: set[tuple[int, int, int]]) -> bool:
    y, mo, d = found
    if y is not None:
        return (y, mo, d) in allowed
    return any(mm == mo and dd == d for _, mm, dd in allowed)


def allowed_dates(workspace: Path) -> set[tuple[int, int, int]]:
    """Dates in the agent-visible inputs plus the 'as of' date in the instruction."""
    out = {(y, m, d) for y, m, d in dates_in(input_text(workspace)) if y is not None}
    for s in fixture().get("extra_allowed_dates", []):
        y, m, d = (int(x) for x in s.split("-"))
        out.add((y, m, d))
    return out


def amounts_in(text: str) -> set[Decimal]:
    """Dollar-scale numbers (>= 1000 after expanding M / million / K suffixes)."""
    out: set[Decimal] = set()
    for m in AMOUNT.finditer(text):
        raw = m.group("n").replace(",", "")
        frac = m.group("f") or "0"
        try:
            val = Decimal(f"{raw}.{frac}")
        except Exception:
            continue
        suf = (m.group("suf") or "").lower()
        if suf in ("m", "mm", "million"):
            val *= 1_000_000
        elif suf == "k":
            val *= 1_000
        val = val.quantize(Decimal("0.01"))
        if val >= 1000:
            out.add(val)
    return out


def has_amount(text: str, amount: str) -> bool:
    """True when the amount (e.g. '3200', '2000000') appears, in any notation."""
    return Decimal(amount).quantize(Decimal("0.01")) in amounts_in(text)


PERCENT_WORDS = {"5": "five", "10": "ten", "15": "fifteen", "100": "one hundred"}


def has_percent(text: str, pct: str) -> bool:
    low = text.lower()
    if re.search(rf"(?<![\d.]){re.escape(pct)}(?:\.0+)?\s?(?:%|percent\b|per cent\b)", low):
        return True
    word = PERCENT_WORDS.get(pct)
    return bool(word and re.search(rf"\b{word}\s+percent\b", low))


def cites_section(text: str, section: str) -> bool:
    """True when the text cites IFB section N (§3, Section 3, Sec. 3) or, for
    'addendum', names the addendum."""
    low = text.lower()
    if section == "addendum":
        return "addend" in low
    n = int(section)
    return re.search(rf"(?:§\s*|\bsections?\s+|\bsec\.?\s*)0?{n}\b(?!\s*\d{{2}})", low) is not None


def logical_lines(text: str) -> list[str]:
    """Merge soft-wrapped continuation lines so one bullet, table row, or
    paragraph is one line to match against. An agent that wraps a bullet at 80
    columns should not be scored differently from one that does not."""
    out: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            out.append("")
            continue
        opens_block = bool(
            stripped.startswith(("|", "#", ">", "```"))
            or re.match(r"^[-*+]\s", stripped)
            or re.match(r"^\d+[.)]\s", stripped)
        )
        prev = out[-1].strip() if out else ""
        prev_closed = prev.startswith(("|", "#", "```"))
        if prev and not opens_block and not prev_closed:
            out[-1] = out[-1].rstrip() + " " + stripped
        else:
            out.append(raw.rstrip())
    return out


def keyword_lines(text: str, keywords: tuple[str, ...]) -> list[str]:
    """Logical lines that mention any of the keywords (case-insensitive)."""
    out = []
    for ln in logical_lines(text):
        low = ln.lower()
        if any(k.lower() in low for k in keywords):
            out.append(ln)
    return out


def section_body(text: str, heading: str) -> str:
    """Body of the '## <heading>' section (case-insensitive) up to the next '## '."""
    low = text.lower()
    start = low.find("## " + heading.lower())
    if start < 0:
        return ""
    end = low.find("\n## ", start + 3)
    return text[start : end if end > 0 else len(text)]


def table_rows(section: str) -> list[str]:
    rows = []
    for ln in section.splitlines():
        s = ln.strip()
        if not s.startswith("|"):
            continue
        if re.match(r"^\|\s*:?-{2,}", s):
            continue
        rows.append(s)
    return rows[1:] if rows else []  # drop the header row


CRITERION_AREAS = (
    r"owner|relationship", r"delivery|contract", r"schedule",
    r"bond|insurance", r"licens|prequal|qualification", r"wage|labor",
    r"scope|fit", r"competition", r"risk allocation", r"document",
)
RATING = re.compile(r"\b(?:favorable|neutral|unfavorable|unknown)\b", re.I)


def rated_criteria_count(text: str) -> int:
    """Count distinct criteria with explicit ratings and explanatory content.

    Accept default table cells or labeled bullets, independent of headings.
    A blank rating or a copied dates table cannot satisfy this check.
    """
    found = set()
    for line in logical_lines(text):
        s = line.strip().replace("**", "")
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) < 3 or not RATING.fullmatch(cells[1]) or not cells[2]:
                continue
            label = cells[0]
        else:
            match = re.match(r"^[-*+]\s+([^:]+):\s*(favorable|neutral|unfavorable|unknown)\b[\s:;,.—–-]+(.+)", s, re.I)
            if not match:
                continue
            label = match[1]
        for i, area in enumerate(CRITERION_AREAS):
            if re.search(area, label, re.I):
                found.add(i)
                break
    return len(found)
