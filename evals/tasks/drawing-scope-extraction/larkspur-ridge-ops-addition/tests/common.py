"""Shared helpers for the larkspur-ridge-ops-addition verifier.

Everything here reads the agent's scope list, the input sheet index, and the
hidden fixture. Nothing here is copied into the agent image.

The truth table below is the corrected candidate set: what the drawing set
actually calls for once the first-pass candidate file has been checked against
the G-000 sheet index. It is derived from
``tests/fixtures/reference-candidates.json`` and the script output in
``tests/fixtures/script-output.md``, not from anything the agent writes.
"""

from __future__ import annotations

import re
from pathlib import Path

SCOPE_LIST = "output/scope-list.md"

# The 18 sheets in the G-000 index. Nothing outside this set may be cited.
SHEETS = (
    "G-000",
    "A-002",
    "C-101",
    "C-201",
    "C-501",
    "S-001",
    "S-101",
    "S-301",
    "A-101",
    "A-102",
    "A-103",
    "A-201",
    "A-301",
    "A-501",
    "A-601",
    "M-101",
    "P-101",
    "E-101",
)

# Sheets the first-pass file cited that are not in the index and not in the
# set. They may be named in an RFI; they may never carry scope.
PHANTOM_SHEETS = ("A-702", "E-401")

SHEET_TOKEN = re.compile(r"\b[A-Z]{1,2}-\d{3}\b")

# Every candidate the corrected file carries, as (keywords, sheet, decision).
# All keywords must appear in the same block as the sheet number.
ITEMS: dict[str, tuple[tuple[str, ...], str, str]] = {
    "temp_barricades": (("barricade", "dust partition"), "G-000", "include"),
    "blocking": (("blocking", "grab bar"), "G-000", "include"),
    "scada_by_others": (("scada panel", "telemetry"), "G-000", "exclude"),
    "asphalt_removal": (("remove", "asphalt pavement"), "C-101", "include"),
    "mass_excavation": (("excavation", "412.50"), "C-101", "include"),
    "sanitary_lateral": (("sanitary sewer lateral", "mh-4"), "C-201", "include"),
    "water_service": (("domestic water service", "backflow"), "C-201", "include"),
    "gas_by_others": (("gas service",), "C-201", "exclude"),
    "service_conduit": (("service conduit", "pull vault"), "C-201", "review"),
    "bollards": (("bollard", "overhead door jamb"), "C-501", "include"),
    "yard_apron": (("aggregate base", "yard apron"), "C-501", "include"),
    "footings": (("footing", "f-1"), "S-101", "include"),
    "slab_on_grade": (("slab on grade", "vapor retarder"), "S-101", "include"),
    "foundation_walls": (("foundation wall", "cast-in-place"), "S-101", "include"),
    "steel_frame": (("hss 6x6", "w12x26"), "S-301", "include"),
    "cmu_screen_wall": (("masonry", "screen wall"), "S-301", "include"),
    "pemb_not_used": (("pre-engineered metal building",), "S-301", "exclude"),
    "siding_removal": (("metal siding", "girt"), "A-101", "include"),
    "hm_door_removal": (("hollow metal door", "3070"), "A-101", "include"),
    "partition_p1": (("partition type p1", "gypsum board"), "A-102", "include"),
    "overhead_doors": (("overhead door", "operator"), "A-102", "include"),
    "doors_per_schedule": (("personnel door", "hardware"), "A-102", "review"),
    "frp_wainscot": (("fiberglass reinforced panel", "wainscot"), "A-102", "include"),
    "tpo_roofing": (("tpo", "membrane roofing"), "A-103", "include"),
    "coping": (("coping", "edge flashing"), "A-103", "include"),
    "metal_wall_panel": (("metal wall panel", "26 gage"), "A-201", "include"),
    "air_barrier": (("air and water barrier", "sheathing"), "A-301", "include"),
    "parapet_nailer": (("nailer", "parapet"), "A-301", "include"),
    "sealed_concrete": (("sealed concrete", "sc-1"), "A-501", "include"),
    "act_ceiling": (("acoustical ceiling tile", "act-1"), "A-501", "include"),
    "rtu_1": (("rooftop unit", "rtu-1"), "M-101", "include"),
    "ef_2": (("exhaust fan", "ef-2"), "M-101", "include"),
    "test_and_balance": (("test and balance",), "M-101", "include"),
    "ddc_by_others": (("thermostat", "ddc"), "M-101", "exclude"),
    "water_closet": (("water closet", "wc-1"), "P-101", "include"),
    "trench_drain": (("trench drain", "interceptor"), "P-101", "include"),
    "panel_la": (("panel la", "225"), "E-101", "include"),
    "conduit_stubups": (("conduit stub-up", "scada"), "E-101", "include"),
    "high_bay": (("high bay", "4000k"), "E-101", "include"),
}

# Work the first pass invented against sheets that do not exist. Each is
# (keywords that must stay out of the scope list, the sheet it was cited to).
UNGROUNDED = {
    "room_signage": (("signage", "room identification"), "A-702"),
    "transfer_switch": (("transfer switch", "standby generator"), "E-401"),
}

# Sheets read that carry no work items, plus the sheet that could not be read.
NO_SCOPE_SHEETS = ("A-002", "S-001")
UNREADABLE_SHEET = "A-601"

# Divisions that carry included scope in the corrected set.
INCLUDED_DIVISIONS = (
    "01",
    "02",
    "03",
    "04",
    "05",
    "06",
    "07",
    "08",
    "09",
    "10",
    "22",
    "23",
    "26",
    "31",
    "32",
    "33",
)

# Wording that marks a sheet reference as a gap being reported rather than a
# citation being made.
NEGATIONS = (
    "not in the sheet index",
    "not in the index",
    "not in the set",
    "not in this set",
    "is not a sheet",
    "does not exist",
    "does not contain",
    "does not appear",
    "no sheet",
    "no such sheet",
    "not issued",
    "missing from the index",
    "not part of the set",
    "rfi",
)


# A line that reports a sheet as missing, dropped, or flagged is not a
# citation. The phrase list above is kept for readability; the regex catches
# the many ways a memo can say the same thing ("do not appear", "neither
# sheet exists", "not found", "sent to RFI").
NEGATION_RE = re.compile(
    r"\b(?:not|no|neither|never|nor|missing|absent|phantom|non-?existent|nonexistent|"
    r"isn'?t|aren'?t|doesn'?t|don'?t|cannot|can'?t|dropped|excluded|removed|omitted|"
    r"rfi|flag(?:ged|s)?|unknown|unresolved|unverified|unreadable|could not|couldn'?t)\b",
    re.IGNORECASE,
)


def is_negated(line: str) -> bool:
    return has_phrase(line, *NEGATIONS) or NEGATION_RE.search(line) is not None


def scope_text(workspace: Path) -> str:
    path = workspace / SCOPE_LIST
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def has_phrase(text: str, *phrases: str) -> bool:
    low = text.lower()
    return any(p.lower() in low for p in phrases)


def has_all(text: str, *phrases: str) -> bool:
    low = text.lower()
    return all(p.lower() in low for p in phrases)


def blocks(text: str) -> list[str]:
    """Split into candidate-sized chunks.

    A block starts at a bullet, a table row, or a heading and runs until the
    next one, so the script's two-line rendering (bullet plus indented
    ``Source:`` line) lands in one block and so does a free-form agent's
    single-line bullet.
    """
    out: list[str] = []
    cur: list[str] = []
    for line in text.splitlines():
        if re.match(r"^\s*[-*+]\s", line) or line.startswith("|") or line.startswith("#"):
            if cur:
                out.append("\n".join(cur))
            cur = [line]
        else:
            cur.append(line)
    if cur:
        out.append("\n".join(cur))
    return out


def section(text: str, heading: str) -> str:
    """The text under a level-2 heading, up to the next level-2 heading."""
    low = text.lower()
    start = low.find(heading.lower())
    if start < 0:
        return ""
    end = low.find("\n## ", start + len(heading))
    return text[start : end if end > 0 else len(text)]


def included_section(text: str) -> str:
    for heading in ("## included scope", "## scope", "## included"):
        found = section(text, heading)
        if found:
            return found
    return ""


def ledger_section(text: str) -> str:
    for heading in ("## coverage ledger", "## coverage", "## ledger", "## sheets reviewed", "## sheet coverage"):
        found = section(text, heading)
        if found:
            return found
    return ""


def item_blocks(text: str, keywords: tuple[str, ...]) -> list[str]:
    """Every block that mentions all of the keywords."""
    out = []
    for block in blocks(text):
        low = block.lower()
        if all(k in low for k in keywords):
            out.append(block)
    return out


def item_block(text: str, keywords: tuple[str, ...]) -> str:
    """The first block that mentions every keyword, or ''."""
    found = item_blocks(text, keywords)
    return found[0] if found else ""


def ledger_row(ledger: str, sheet: str) -> str:
    """The ledger row whose first cell is this sheet, else any block naming it."""
    for line in ledger.splitlines():
        if re.match(rf"^\|\s*{re.escape(sheet)}\s*\|", line, re.IGNORECASE):
            return line
    return item_block(ledger, (sheet.lower(),))


def cited_with_sheet(text: str, keywords: tuple[str, ...], sheet: str) -> bool:
    for block in blocks(text):
        low = block.lower()
        if all(k in low for k in keywords) and sheet.lower() in low:
            return True
    return False


def citation_lines(text: str) -> list[str]:
    """Lines that make a citation rather than describe a gap.

    A citation line is a ``Source:`` line, a ledger table row whose first cell
    is a sheet number, or a scope bullet. When the agent wrote something with
    no recognizable citation lines, fall back to every line that is not
    reporting a missing sheet.
    """
    lines = [line for line in text.splitlines() if not is_negated(line)]
    picked = [
        line
        for line in lines
        if "source:" in line.lower()
        or re.match(r"^\|\s*[A-Za-z]{1,2}-\d{3}\s*\|", line)
        or re.match(r"^\s*[-*+]\s+\*\*", line)
    ]
    return picked if len(picked) >= 5 else lines


def grounded_lines(text: str) -> list[str]:
    """Every line that is not reporting a missing sheet."""
    return [line for line in text.splitlines() if not is_negated(line)]


def sheet_ids(text: str) -> list[str]:
    return SHEET_TOKEN.findall(text)
