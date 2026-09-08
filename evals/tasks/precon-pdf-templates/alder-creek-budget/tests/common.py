"""Shared helpers for the alder-creek-budget verifier.

Everything here reads the agent's output document and the hidden fixture.
Nothing here is copied into the agent image. Parsing is stdlib only
(``html.parser``); no third-party HTML library is used.
"""

from __future__ import annotations

import json
import re
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from pathlib import Path

DOC = "output/budget-export.html"
INPUTS = ("input/alder-creek-budget-export.csv", "input/handoff-notes.md")
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "budget-truth.json"

SKIP_TAGS = {"style", "script", "head", "title", "meta", "link"}
VOID_TAGS = {"br", "hr", "img", "meta", "link", "input", "col", "source"}

NUMBER = re.compile(r"(?<![\d.])(\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?(?![\d])")


class _Doc(HTMLParser):
    """Collects visible text plus the structural facts the format checks need."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.error_count = 0
        self.chunks: list[str] = []
        self.tags: list[str] = []
        self.classes: set[str] = set()
        self.headings: list[str] = []
        self._skip = 0
        self._heading: list[str] | None = None

    # -- parsing ---------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        self.tags.append(tag)
        if tag == "body":
            # An unclosed <head> must not swallow the whole document.
            self._skip = 0
        for key, value in attrs:
            if key == "class" and value:
                self.classes.update(value.split())
        if tag in SKIP_TAGS and tag not in VOID_TAGS:
            self._skip += 1
        if tag in ("h1", "h2", "h3"):
            self._heading = []

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in SKIP_TAGS and tag not in VOID_TAGS and self._skip:
            self._skip -= 1
        if tag in ("h1", "h2", "h3") and self._heading is not None:
            self.headings.append(" ".join(self._heading).strip())
            self._heading = None

    def handle_data(self, data):
        if self._skip:
            return
        text = data.strip()
        if not text:
            return
        self.chunks.append(text)
        if self._heading is not None:
            self._heading.append(text)

    # -- results ---------------------------------------------------------
    @property
    def text(self) -> str:
        return "\n".join(self.chunks)


def raw_html(workspace: Path) -> str:
    path = workspace / DOC
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def parse(workspace: Path) -> _Doc:
    doc = _Doc()
    html = raw_html(workspace)
    if html:
        doc.feed(html)
        doc.close()
    return doc


def doc_text(workspace: Path) -> str:
    """Visible text of the document, with <style> and <head> content dropped."""
    return parse(workspace).text


def side_notes(workspace: Path) -> str:
    """Every Markdown file the agent left in /app/output, concatenated."""
    out = workspace / "output"
    if not out.is_dir():
        return ""
    parts = []
    for path in sorted(out.glob("*.md")):
        parts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


class _Styles(HTMLParser):
    """Read inline CSS and linked flat sibling CSS in document order.

    This is a bounded fixture heuristic, not a browser CSS engine. It does
    not resolve imports, media conditions, specificity, or inline overrides.
    """
    def __init__(self, workspace: Path):
        super().__init__()
        self.output = workspace / "output"
        self.parts = []
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "style":
            self.in_style = True
        if tag == "link" and "stylesheet" in attrs.get("rel", "").split():
            href = attrs.get("href", "")
            if href and Path(href).name == href and href.endswith(".css"):
                path = self.output / href
                if path.is_file() and path.resolve().parent == self.output.resolve():
                    self.parts.append(path.read_text(encoding="utf-8"))

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False

    def handle_data(self, data):
        if self.in_style:
            self.parts.append(data)


def style_sources(workspace: Path) -> str:
    parser = _Styles(workspace)
    parser.feed(raw_html(workspace))
    return re.sub(r"/\*.*?\*/", "", "\n".join(parser.parts), flags=re.S).lower()


def theme_values(workspace: Path) -> set[str]:
    # Same-specificity :root declarations use their last value. This accepts
    # the documented linked override without treating unused old colors as active.
    values = {}
    for block in re.findall(r":root\s*\{([^}]*)\}", style_sources(workspace)):
        for key, value in re.findall(r"(--[\w-]+)\s*:\s*([^;]+)", block):
            values[key] = value.strip()
    return set(values.values())


def input_text(workspace: Path) -> str:
    parts = []
    for name in INPUTS:
        path = workspace / name
        if path.is_file():
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def truth() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def norm(text: str) -> str:
    """Strip currency punctuation so 294,100.00 and $294,100 and 294100 all match."""
    return text.replace("$", "").replace(",", "")


def has_amount(text: str, amount: str) -> bool:
    """True when the amount appears as a number, with or without .00 cents."""
    n = norm(text)
    base = amount[:-3] if amount.endswith(".00") else amount
    base = base.lstrip("-")
    pattern = rf"(?<![\d.]){re.escape(base)}(?:\.00)?(?![\d])"
    return re.search(pattern, n) is not None


def has_all(text: str, *amounts: str) -> bool:
    return all(has_amount(text, a) for a in amounts)


def has_phrase(text: str, *phrases: str) -> bool:
    low = text.lower()
    return any(p.lower() in low for p in phrases)


def words(text: str) -> str:
    """Lowercase, drop punctuation, collapse whitespace.

    Lets 'Heating, Ventilating, and Air Conditioning' match the export's
    'Heating Ventilating and Air Conditioning'.
    """
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9%]+", " ", text.lower())).strip()


def has_words(haystack: str, needle: str) -> bool:
    return words(needle) in words(haystack)


def document_amounts(workspace: Path) -> set[Decimal]:
    """Dollar-scale figures in the document's visible text.

    Style blocks are already dropped by the parser, so hex colors, point
    sizes, and page dimensions never reach this set. Anything under 1,000 is
    ignored: those are division codes, quantities, years, and percentages,
    not budget figures.
    """
    return numbers(norm(doc_text(workspace)), 1000)


def allowed_amounts(workspace: Path) -> set[Decimal]:
    """Every figure a grounded document may print.

    The export and the handoff notes, plus the hidden fixture's arithmetic
    (line-item sums, the Division 09 gap), plus pairwise sums and
    differences of the large ones so legitimate arithmetic is not
    penalized.
    """
    text = input_text(workspace)
    if FIXTURE.is_file():
        text += "\n" + FIXTURE.read_text(encoding="utf-8")
    base = numbers(norm(text))
    big = sorted(n for n in base if n >= 1000)
    derived: set[Decimal] = set()
    for i, a in enumerate(big):
        for b in big[i + 1 :]:
            derived.add(abs(a - b))
            derived.add(a + b)
    for n in big:
        derived.add((n * Decimal("0.10")).quantize(Decimal("0.01")))
        derived.add((n * Decimal("0.05")).quantize(Decimal("0.01")))
    return base | derived


def numbers(text: str, minimum: Decimal | int = 0) -> set[Decimal]:
    """Every number in the text, as Decimal, at or above ``minimum``."""
    floor = Decimal(minimum)
    out: set[Decimal] = set()
    for match in NUMBER.finditer(text):
        raw = match.group(0).replace(",", "")
        try:
            value = Decimal(raw).quantize(Decimal("0.01"))
        except InvalidOperation:
            continue
        if value >= floor:
            out.add(value)
    return out
