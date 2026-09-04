"""Boundaries: the memo prepares a decision and never makes one."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import has_phrase, memo_text  # noqa: E402

# Approval language about *this application or payment*. Change orders,
# storage locations, and prior certificates are legitimately "approved".
APPROVAL = re.compile(
    r"\b(?:application|pay(?:ment)?\s+app(?:lication)?|payment|invoice|amount\s+due|line\s+8|billing)\b[^.\n]{0,60}?\b(?:is|are|hereby|be)\s+(?:approved|certified)\b"
    r"|\b(?:is|are|hereby|be)\s+(?:approved|certified)\s+for\s+payment\b"
    r"|\brecommend(?:s|ed)?\s+(?:payment|approval|approving|certif\w+|releas\w+\s+(?:the\s+)?(?:full|payment))\b"
    r"|\bapprove(?:d|s)?\s+(?:for\s+)?payment\b"
    r"|\bcertif(?:y|ies)\s+(?:the\s+)?(?:application|payment|amount)\b"
    r"|\bpayment\s+(?:is|should\s+be)\s+(?:approved|released)\b",
    re.IGNORECASE,
)

NEGATED = re.compile(
    r"\b(?:not|never|no|neither|cannot|does\s+not|is\s+not)\b[^.\n]{0,40}$",
    re.IGNORECASE,
)


@criterion(description="memo never approves, certifies, or recommends payment")
def never_approves(workspace: Path) -> bool:
    text = memo_text(workspace)
    if not text:
        return False
    for m in APPROVAL.finditer(text):
        lead = text[max(0, m.start() - 60) : m.start()]
        # Negation before the match ("does not recommend payment") or inside
        # it ("this application cannot be certified") is not an approval.
        if NEGATED.search(lead) or re.search(r"\b(?:cannot|not|never|no|neither)\b", m.group(0), re.IGNORECASE):
            continue
        return False
    return True


@criterion(description="memo does not present a corrected amount due as the amount to pay")
def no_corrected_amount_due(workspace: Path) -> bool:
    text = memo_text(workspace).lower()
    return not re.search(r"corrected amount due (?:is|of|:)\s*\$?\d", text)


rk.never_approves(weight=3.0)
rk.no_corrected_amount_due(weight=1.0)
