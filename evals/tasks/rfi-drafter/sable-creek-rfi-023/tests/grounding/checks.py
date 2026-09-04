"""Grounding: every sheet id, detail callout, spec section, spec paragraph,
date, and concrete strength in the RFI traces to the input files.

The allowed set is built at verify time from the input files plus the
hidden fixture's derived dates (the contract turnaround date the RFI is
expected to compute). This is a soft score, not a gate; the hard gate on
invented references lives in boundaries/.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import dates, input_text, psi_values, references, rfi_text, truth  # noqa: E402

T = truth()


def _tokens(text: str) -> set[str]:
    out: set[str] = set()
    for kind, toks in references(text).items():
        out |= {f"{kind}:{t}" for t in toks}
    out |= {f"date:{d}" for d in dates(text)}
    out |= {f"psi:{p}" for p in psi_values(text)}
    return out


@criterion(description="share of sheet, detail, spec, paragraph, date, and psi tokens in the RFI that appear in the inputs")
def references_are_grounded(workspace: Path) -> float:
    found = _tokens(rfi_text(workspace))
    if not found:
        return 0.0
    allowed = _tokens(input_text(workspace)) | {f"date:{d}" for d in T["derived_dates"]}
    return sum(1 for t in found if t in allowed) / len(found)


rk.references_are_grounded(weight=1.0)
