"""Shared helpers for the harborview-app3 verifier.

Everything here reads the agent's memo and the hidden fixture. Nothing here
is copied into the agent image.
"""

from __future__ import annotations

import re
from pathlib import Path

MEMO = "output/review-memo.md"


def memo_text(workspace: Path) -> str:
    path = workspace / MEMO
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def norm(text: str) -> str:
    """Strip currency punctuation so 3,500.00 and $3,500 and 3500 all match."""
    return text.replace("$", "").replace(",", "")


def has_amount(text: str, amount: str) -> bool:
    """True when the amount (e.g. '3500', '3500.00', '103.85') appears as a number."""
    n = norm(text)
    base = amount[:-3] if amount.endswith(".00") else amount
    pattern = rf"(?<![\d.]){re.escape(base)}(?:\.00)?(?![\d])"
    return re.search(pattern, n) is not None


def has_all(text: str, *amounts: str) -> bool:
    return all(has_amount(text, a) for a in amounts)


def has_phrase(text: str, *phrases: str) -> bool:
    low = text.lower()
    return any(p.lower() in low for p in phrases)
