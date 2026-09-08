"""Correctness: are the leveled totals, the gaps, the plugs, the ranking, and
the planted bid-form and bond problems all in the comparison?

Truth comes from tests/fixtures/script-output.md (level_bids.py run on the
three hidden reference extractions and the estimator decisions file the agent
was given) and the planted problems listed in Task.md. Nothing here trusts the
comparison's own claims about what it checked.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rewardkit as rk  # noqa: E402
from rewardkit import criterion  # noqa: E402

from common import (  # noqa: E402
    comparison_text,
    has_all,
    has_amount,
    has_phrase,
    line_states_amount,
    lines_mentioning,
)

# Leveled total = base bid + plugs + adjustments, from the hidden fixture.
# Ironwood 612,400 + 6,850. Blue Heron 571,900 + 38,600 + 4,200 (incomplete,
# one gap unresolved). Cardinal 598,750 + 9,500 - 27,400.
LEVELED_TOTALS = {
    "Ironwood": 619250,
    "Blue Heron": 614700,
    "Cardinal": 580850,
}

# Each plug and the one adjustment: the scope, the bidder it applies to, and
# its amount, all named together.
PLUGS = {
    "ironwood_roof_hatch": ("roof hatch", "Ironwood", "6850"),
    "blue_heron_vapor_retarder": ("vapor retarder", "Blue Heron", "38600"),
    "blue_heron_walkway_pads": ("walkway", "Blue Heron", "4200"),
    "cardinal_hoisting": ("hoisting", "Cardinal", "9500"),
    "cardinal_panel_adjustment": ("metal wall panel", "Cardinal", "27400"),
}

# Each base-scope gap: the scope, the bidder, and the status, all on one line.
GAPS = {
    "blue_heron_vapor_retarder": (("vapor retarder",), "Blue Heron", ("excluded",)),
    "blue_heron_walkway_pads": (("walkway",), "Blue Heron", ("omitted", "silent")),
    "blue_heron_ndl_warranty": (("warranty",), "Blue Heron", ("unknown", "unresolved")),
    "cardinal_hoisting": (("hoisting",), "Cardinal", ("excluded", "by gc")),
    "ironwood_roof_hatch": (("roof hatch",), "Ironwood", ("excluded", "by others")),
}


@criterion(description="comparison exists at output/leveled-comparison.md and is not trivial")
def comparison_exists(workspace: Path) -> bool:
    return len(comparison_text(workspace)) > 2000


@criterion(description="share of bidders whose leveled total matches the fixture within $1")
def leveled_totals(workspace: Path) -> float:
    text = comparison_text(workspace)
    if not text:
        return 0.0
    hits = sum(1 for name, amount in LEVELED_TOTALS.items() if line_states_amount(text, name, amount))
    return hits / len(LEVELED_TOTALS)


@criterion(description="every bidder's leveled total matches the fixture within $1")
def all_leveled_totals_match(workspace: Path) -> bool:
    text = comparison_text(workspace)
    if not text:
        return False
    return all(line_states_amount(text, name, amount) for name, amount in LEVELED_TOTALS.items())


@criterion(description="ranking leads with the lowest complete leveled total and calls Blue Heron incomplete")
def leveled_ranking(workspace: Path) -> bool:
    text = comparison_text(workspace)
    if not text:
        return False
    # Ranking is substantive; the exact headline and headings are format diagnostics.
    headline = [line for line in text.splitlines()[:20]
                if has_phrase(line, "lowest") and has_phrase(line, "complete", "fully scoped")
                and has_phrase(line, "leveled", "leveling")]
    if not any("cardinal" in line.lower() and has_amount(line, "580850") for line in headline):
        return False
    for line in lines_mentioning(text, "lowest"):
        low = line.lower()
        # A correct comparison can explicitly contrast the raw low with the leveled low.
        if "blue heron" in low and not has_phrase(low, "base", "raw", "incomplete", "unresolved"):
            return False
    incomplete = lines_mentioning(text, "Blue Heron")
    return any(("incomplete" in ln.lower() or "unresolved" in ln.lower()) for ln in incomplete)


@criterion(description="each plug and the adjustment named with its scope, its bidder, and its amount")
def plugs_and_adjustment(workspace: Path) -> float:
    text = comparison_text(workspace)
    if not text:
        return 0.0
    hits = 0
    for scope, bidder, amount in PLUGS.values():
        if any(has_amount(line, amount) for line in lines_mentioning(text, scope, bidder)):
            hits += 1
    return hits / len(PLUGS)


@criterion(description="each base-scope gap named with its bidder and its status")
def gaps_named(workspace: Path) -> float:
    text = comparison_text(workspace)
    if not text:
        return 0.0
    hits = 0
    for scope_phrases, bidder, statuses in GAPS.values():
        found = False
        for scope in scope_phrases:
            for line in lines_mentioning(text, scope, bidder):
                if has_phrase(line, *statuses):
                    found = True
                    break
            if found:
                break
        if found:
            hits += 1
    return hits / len(GAPS)


@criterion(description="planted bid form footing error and mismatched bond bases are flagged")
def planted_flags(workspace: Path) -> float:
    text = comparison_text(workspace)
    if not text:
        return 0.0
    hits = 0
    # Cardinal's bid form: rows 1-13 sum to 600,550 against a stated 598,750.
    if has_all(text, "600550", "598750", "1800"):
        hits += 1
    # Bonds are on three different bases and are not in any leveled total.
    if has_phrase(text, "bond") and has_all(text, "8900") and has_phrase(text, "1.5"):
        hits += 1
    return hits / 2


# The leveled totals are the deliverable, so the all-or-nothing check on them
# carries the most weight inside this dimension: a comparison that misses one
# gap keeps a wrong total and cannot reach the reward threshold on the others.
rk.comparison_exists(weight=1.0)
rk.leveled_totals(weight=1.0)
rk.all_leveled_totals_match(weight=10.0)
rk.leveled_ranking(weight=10.0)
rk.plugs_and_adjustment(weight=3.0)
rk.gaps_named(weight=3.0)
rk.planted_flags(weight=2.0)
