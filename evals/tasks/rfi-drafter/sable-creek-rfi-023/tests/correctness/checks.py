"""Correctness: does the RFI state the planted conflict with both sources,
propose the resolution the documents support, and carry the number, the
response date, and the log row?

Truth comes from tests/fixtures/truth.json and Task.md. Nothing here trusts
the RFI's own claims about what it reviewed.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import dates, has_phrase, has_psi, log_rows, rfi_text, section, truth  # noqa: E402

T = truth()


@criterion(description="RFI exists at output/rfi-023.md and is not trivial")
def rfi_exists(workspace: Path) -> bool:
    return len(rfi_text(workspace)) > 1500


@criterion(description="both sides of the conflict cited: S-001 Note 5, 03 30 00 paragraph 2.6.C, the returned M-2 submittal, and 3/S-101")
def conflict_sources_cited(workspace: Path) -> float:
    text = rfi_text(workspace)
    if not text:
        return 0.0
    low = text.lower()
    checks = (
        "s-001" in low and re.search(r"\bnote\s*5\b", low) is not None,
        "03 30 00" in low and "2.6.c" in low,
        ("03 30 00-02" in low or re.search(r"\bm-2\b", low) is not None) and "no exceptions taken" in low,
        "3/s-101" in low,
    )
    return sum(checks) / len(checks)


@criterion(description="both strengths stated: 3,500 psi and 4,000 psi")
def strengths_stated(workspace: Path) -> bool:
    text = rfi_text(workspace)
    return has_psi(text, "3500") and has_psi(text, "4000")


@criterion(description="question section leads with the specific ask (please confirm / please advise)")
def question_leads_with_ask(workspace: Path) -> bool:
    body = section(rfi_text(workspace), "Question").strip()
    if not body:
        return False
    first = body.splitlines()[0].strip().lower()
    return re.match(r"(?:please\s+(?:confirm|advise)|(?:could|would) you\s+(?:please\s+)?confirm|confirm whether)\b", first) is not None


@criterion(description="suggested resolution proposes 4,000 psi per 2.6.C and is not withheld")
def resolution_proposed(workspace: Path) -> bool:
    body = section(rfi_text(workspace), "Suggested resolution")
    if not body.strip():
        return False
    if has_phrase(body, "none proposed"):
        return False
    low = body.lower()
    # The basis may be cited as the spec paragraph or as the precedence note.
    return has_psi(body, T["expected_resolution_psi"]) and ("2.6.c" in low or "note 1" in low)


@criterion(description="precedence note S-001 Note 1 (more stringent governs) cited as the basis")
def precedence_note_cited(workspace: Path) -> bool:
    low = rfi_text(workspace).lower()
    return re.search(r"\bnote\s*1\b", low) is not None and "stringent" in low


@criterion(description="response needed by is the user's date, 2026-10-19, in the header")
def response_date_present(workspace: Path) -> bool:
    text = rfi_text(workspace)
    for ln in text.splitlines():
        if ln.strip().startswith("|") and "response needed by" in ln.lower():
            return T["response_needed_by"] in dates(ln)
    return False


@criterion(description="RFI number from the user, RFI-023, in the title line")
def rfi_number_present(workspace: Path) -> bool:
    text = rfi_text(workspace).lstrip()
    first = text.splitlines()[0] if text else ""
    return first.startswith("# ") and T["rfi_number"].lower() in first.lower()


@criterion(description="log row present with number, To firm, needed-by date, Open status, potential impacts, and related sheets")
def log_row_present(workspace: Path) -> float:
    rows = log_rows(rfi_text(workspace), T["rfi_number"])
    if not rows:
        return 0.0
    best = 0.0
    for row in rows:
        joined = " | ".join(row)
        low = joined.lower()
        checks = (
            len(row) >= 11,
            T["to_firm"].lower() in low,
            T["response_needed_by"] in dates(joined),
            re.search(r"\|\s*open\s*\|", "| " + joined + " |", re.IGNORECASE) is not None,
            low.count("potential") >= 2,
            "s-001" in low and "03 30 00" in low,
        )
        best = max(best, sum(checks) / len(checks))
    return best


@criterion(description="says the needed-by date is shorter than the 14-day contract turnaround")
def turnaround_flagged(workspace: Path) -> bool:
    text = rfi_text(workspace)
    low = text.lower()
    return T["contract_turnaround_date"] in dates(text) or (
        "14" in low and "turnaround" in low and has_phrase(low, "shorter", "less than", "sooner")
    )


rk.rfi_exists(weight=1.0)
rk.conflict_sources_cited(weight=3.0)
rk.strengths_stated(weight=2.0)
rk.question_leads_with_ask(weight=1.0)
rk.resolution_proposed(weight=4.0)
rk.precedence_note_cited(weight=2.0)
rk.response_date_present(weight=2.0)
rk.rfi_number_present(weight=1.0)
rk.log_row_present(weight=3.0)
rk.turnaround_flagged(weight=1.0)
