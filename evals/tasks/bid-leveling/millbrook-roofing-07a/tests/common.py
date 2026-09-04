"""Shared helpers for the millbrook-roofing-07a verifier.

Everything here reads the agent's leveled comparison and the hidden fixtures.
Nothing here is copied into the agent image.
"""

from __future__ import annotations

import re
from decimal import Decimal
from itertools import combinations
from pathlib import Path

COMPARISON = "output/leveled-comparison.md"

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SCRIPT_OUTPUT = FIXTURES / "script-output.md"

# Short, unambiguous aliases for the three bidders. Every bidder line in a
# comparison names at least one of these.
BIDDERS = {
    "ironwood": "Ironwood",
    "blue_heron": "Blue Heron",
    "cardinal": "Cardinal",
}

NUMBER = re.compile(r"(?<![\d.])(\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?(?![\d])")


def comparison_text(workspace: Path) -> str:
    path = workspace / COMPARISON
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def norm(text: str) -> str:
    """Strip currency punctuation so 38,600.00 and $38,600 and 38600 all match."""
    return text.replace("$", "").replace(",", "")


def has_amount(text: str, amount: str) -> bool:
    """True when the amount (e.g. '38600', '6850.00', '1.5') appears as a number."""
    n = norm(text)
    base = amount[:-3] if amount.endswith(".00") else amount
    pattern = rf"(?<![\d.]){re.escape(base)}(?:\.00)?(?![\d])"
    return re.search(pattern, n) is not None


def has_all(text: str, *amounts: str) -> bool:
    return all(has_amount(text, a) for a in amounts)


def has_phrase(text: str, *phrases: str) -> bool:
    low = text.lower()
    return any(p.lower() in low for p in phrases)


def lines_mentioning(text: str, *phrases: str) -> list[str]:
    """Lines that contain every one of the phrases (case-insensitive)."""
    out = []
    for line in text.splitlines():
        low = line.lower()
        if all(p.lower() in low for p in phrases):
            out.append(line)
    return out


def line_states_amount(text: str, phrase: str, amount: int, tolerance: int = 1) -> bool:
    """True when some line naming ``phrase`` carries a number within ``tolerance``
    dollars of ``amount``. Leveled totals are checked this way so the bidder and
    the number have to sit together, not merely both appear in the document."""
    target = Decimal(amount)
    tol = Decimal(tolerance)
    for line in lines_mentioning(text, phrase):
        for value in numbers(norm(line)):
            if abs(value - target) <= tol:
                return True
    return False


def numbers(text: str) -> set[Decimal]:
    out: set[Decimal] = set()
    for m in NUMBER.finditer(text):
        raw = m.group(0).replace(",", "")
        try:
            out.add(Decimal(raw).quantize(Decimal("0.01")))
        except Exception:
            pass
    return out


def allowed_amounts(workspace: Path) -> set[Decimal]:
    """Every number the comparison may legitimately state: the numbers in the
    agent's inputs, the numbers in the hidden script output, and the pairwise
    sums and differences of those, so leveling arithmetic is not penalised."""
    text = ""
    input_dir = workspace / "input"
    if input_dir.is_dir():
        for path in sorted(input_dir.iterdir()):
            if path.is_file():
                text += path.read_text(encoding="utf-8", errors="replace") + "\n"
    if SCRIPT_OUTPUT.is_file():
        text += SCRIPT_OUTPUT.read_text(encoding="utf-8") + "\n"
    base = numbers(text)
    # The decisions file states cents; a comparison states dollars.
    base |= {(n / Decimal(100)).quantize(Decimal("0.01")) for n in base if n >= 1000}
    big = {n for n in base if n >= 1000}
    derived: set[Decimal] = set()
    for a, b in combinations(sorted(big), 2):
        derived.add(abs(a - b))
        derived.add(a + b)
    # Three-term arithmetic is also legitimate leveling work, e.g. a bid
    # form's rows 1-10 stated as total minus two excluded rows.
    if len(big) <= 160:
        for a, b, c in combinations(sorted(big), 3):
            derived.add(a + b + c)
            derived.add(abs(a + b - c))
            derived.add(abs(a - b + c))
            derived.add(abs(a - b - c))
    return base | derived


def stated_amounts(text: str) -> set[Decimal]:
    """Dollar-scale figures in the comparison. Item numbers, spec sections,
    percentages, unit prices, and counts are below the cut."""
    return {n for n in numbers(norm(text)) if n >= 1000}
