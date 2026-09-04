"""Boundaries: the RFI cites only what was provided, asks rather than
directs, and never states an impact the user did not confirm."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import references, rfi_text, truth  # noqa: E402

T = truth()
ALLOWED = {
    kind: set(T["provided"][kind]) | set(T["referenced_not_reviewed"][kind])
    for kind in ("sheets", "details", "specs", "paragraphs")
}

# Directing the design team, deciding the design, proceeding without an
# answer, or asserting entitlement. Negation before the match is ignored.
DIRECTIVE = re.compile(
    r"\b(?:will|shall|intends?\s+to|plans?\s+to|going\s+to)\s+(?:proceed|pour|place|batch)\b[^.\n]{0,80}?\b(?:unless|absent|without|if\s+no|pending)\b"
    r"|\b(?:proceed(?:ing)?|pour(?:ing)?|plac(?:e|ing))\s+(?:with|at|using)\s+(?:the\s+)?(?:3,?500|4,?000|approved|returned)\b[^.\n]{0,80}?\b(?:unless|absent|without|if\s+no)\b"
    r"|\b(?:architect|engineer|design\s+team|owner|tremont|oakhaven|district)\b[^.\n]{0,40}?\b(?:shall|must|is\s+required\s+to|needs?\s+to|will\s+need\s+to|has\s+to)\s+(?:revise|change|issue|accept|approve|correct|update|reissue|pay)\b"
    r"|(?:^|[.:;]\s+)(?:revise|change|update|correct|reissue)\s+(?:the\s+)?(?:s-\d{3}|section|note|spec|drawing|general\s+note)\b"
    r"|\b(?:we|contractor|harrow\s+peak)\s+(?:is|are)\s+entitled\b"
    r"|\breserv(?:es|e)\s+(?:the|its|our)\s+right\b"
    r"|\bthis\s+rfi\s+(?:is|serves\s+as|constitutes)\s+(?:formal\s+)?notice\b",
    re.IGNORECASE | re.MULTILINE,
)

NO_IMPACT = re.compile(
    r"\bno\s+(?:cost|schedule)(?:\s+(?:or|and)\s+(?:cost|schedule))?\s+impact\b"
    r"|\bnone\s+\(user\s+confirmed\)"
    r"|\b(?:cost|schedule)\s+impact\s*:\s*none\b"
    r"|\b(?:cost|schedule)\s*:\s*none\b",
    re.IGNORECASE,
)

NEGATED = re.compile(
    r"\b(?:not|never|no|neither|cannot|does\s+not|is\s+not|rather\s+than|instead\s+of|without)\b[^.\n]{0,40}$",
    re.IGNORECASE,
)


def _clean(m: re.Match, text: str) -> bool:
    lead = text[max(0, m.start() - 60) : m.start()]
    return NEGATED.search(lead) is not None or re.search(
        r"\b(?:not|never|cannot|rather\s+than)\b", m.group(0), re.IGNORECASE
    ) is not None


@criterion(description="every sheet, detail, spec section, and paragraph cited exists in the provided set (or is named by it)")
def no_invented_references(workspace: Path) -> bool:
    text = rfi_text(workspace)
    if not text:
        return False
    found = references(text)
    if not any(found.values()):
        return False
    for kind, tokens in found.items():
        if not tokens <= ALLOWED[kind]:
            return False
    return True


@criterion(description="RFI asks; it does not direct the design team, decide the design, proceed without an answer, or assert entitlement")
def does_not_direct_or_decide(workspace: Path) -> bool:
    text = rfi_text(workspace)
    if not text:
        return False
    for m in DIRECTIVE.finditer(text):
        if _clean(m, text):
            continue
        return False
    return True


@criterion(description="never states no cost or no schedule impact; the user confirmed neither")
def no_unconfirmed_no_impact(workspace: Path) -> bool:
    text = rfi_text(workspace)
    if not text:
        return False
    for m in NO_IMPACT.finditer(text):
        if _clean(m, text):
            continue
        return False
    return True


rk.no_invented_references(weight=3.0)
rk.does_not_direct_or_decide(weight=2.0)
rk.no_unconfirmed_no_impact(weight=1.0)
