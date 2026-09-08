"""Actionable hold rows, independently of the section heading."""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rewardkit as rk
from rewardkit import criterion
from common import memo_text

@criterion(description="hold table contains at least six sourced clearance actions")
def hold_list_rows(workspace: Path) -> bool:
    rows = []
    active = False
    for line in memo_text(workspace).splitlines():
        if not line.strip().startswith("|"):
            active = False
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        low = line.lower()
        if "amount in question" in low and "what would clear" in low:
            active = True
            continue
        if active and len(cells) >= 6 and not all(re.fullmatch(r"[: -]*", c) for c in cells):
            if all(cells[1:6]):
                rows.append(cells)
    return len(rows) >= 6

rk.hold_list_rows(weight=1.0)
