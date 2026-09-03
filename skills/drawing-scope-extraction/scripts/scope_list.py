#!/usr/bin/env python3
"""Print a scope list, grouped by CSI division, from a candidates file.

Usage:
    python3 scripts/scope_list.py candidates.json
    python3 scripts/scope_list.py samples/input-candidates.json

The input is a JSON file in the shape described by
references/candidate-schema.json: the candidates recorded while reading a
drawing set, the assumptions, exclusions, and RFIs kept separately, and the
coverage ledger that lists every sheet and probe.

The script validates the file, then prints Markdown to stdout with these
sections: Included scope, Assumptions, Exclusions (by others), RFIs / review
items, and a Coverage ledger. It never adds scope, quantities, or prices.
Validation errors are printed to stderr and the script exits non-zero.
Standard library only.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

# MasterFormat 2018 divisions, matching references/csi-divisions.md.
# Reserved division numbers are deliberately absent so they fail validation.
DIVISIONS = {
    "00": "Procurement and Contracting Requirements",
    "01": "General Requirements",
    "02": "Existing Conditions",
    "03": "Concrete",
    "04": "Masonry",
    "05": "Metals",
    "06": "Wood, Plastics, and Composites",
    "07": "Thermal and Moisture Protection",
    "08": "Openings",
    "09": "Finishes",
    "10": "Specialties",
    "11": "Equipment",
    "12": "Furnishings",
    "13": "Special Construction",
    "14": "Conveying Equipment",
    "21": "Fire Suppression",
    "22": "Plumbing",
    "23": "Heating, Ventilating, and Air Conditioning (HVAC)",
    "25": "Integrated Automation",
    "26": "Electrical",
    "27": "Communications",
    "28": "Electronic Safety and Security",
    "31": "Earthwork",
    "32": "Exterior Improvements",
    "33": "Utilities",
    "34": "Transportation",
    "35": "Waterway and Marine Construction",
    "40": "Process Interconnections",
    "41": "Material Processing and Handling Equipment",
    "42": "Process Heating, Cooling, and Drying Equipment",
    "43": "Process Gas and Liquid Handling, Purification, and Storage Equipment",
    "44": "Pollution and Waste Control Equipment",
    "45": "Industry-Specific Manufacturing Equipment",
    "46": "Water and Wastewater Equipment",
    "48": "Electrical Power Generation",
}

CANDIDATE_REQUIRED = (
    "id",
    "division",
    "candidate",
    "sheet_number",
    "location",
    "quote",
    "support_level",
    "decision",
    "reason",
)
SUPPORT_LEVELS = (
    "direct",
    "schedule",
    "spec_requirement",
    "reference_only",
    "by_others",
    "inferred",
)
DECISIONS = ("include", "exclude", "review")
# These support levels can never be included on their own; see
# references/grounding-rules.md.
NEVER_INCLUDE = ("reference_only", "by_others", "inferred")

LEDGER_REQUIRED = ("kind", "source", "status", "reason")
LEDGER_KINDS = ("sheet", "probe", "source")
SHEET_STATUSES = ("reviewed", "reviewed_ocr", "unreadable", "not_reviewed")
PROBE_STATUSES = ("covered", "merged", "excluded", "reference_only", "needs_followup", "no_hits")
SOURCE_STATUSES = ("covered", "merged", "excluded", "reference_only", "needs_followup")
NOTE_REQUIRED = ("text", "source")


# --------------------------------------------------------------------------
# Loading and validation
# --------------------------------------------------------------------------


def load(path: Path) -> dict:
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        fail([f"file not found: {path}"])
    except json.JSONDecodeError as error:
        fail([f"{path} is not valid JSON: {error}"])
    if not isinstance(data, dict):
        fail([f"{path}: top level must be a JSON object"])
    return data


def fail(errors: list[str]) -> None:
    print("candidates file failed validation:", file=sys.stderr)
    for error in errors:
        print(f"  - {error}", file=sys.stderr)
    sys.exit(1)


def non_empty_string(value: object) -> bool:
    return isinstance(value, str) and value.strip() != ""


def validate(data: dict) -> list[str]:
    errors: list[str] = []

    for key in ("set_name", "candidates", "coverage_ledger"):
        if key not in data:
            errors.append(f"missing top-level key '{key}'")
    if errors:
        return errors
    if not non_empty_string(data["set_name"]):
        errors.append("set_name must be a non-empty string")
    if not isinstance(data["candidates"], list):
        errors.append("candidates must be a list")
    if not isinstance(data["coverage_ledger"], list):
        errors.append("coverage_ledger must be a list")
    if errors:
        return errors

    # Ledger first: it defines the sheet inventory the candidates cite.
    sheets: dict[str, dict] = {}
    for index, entry in enumerate(data["coverage_ledger"]):
        label = f"coverage_ledger[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label}: must be an object")
            continue
        missing = [key for key in LEDGER_REQUIRED if not non_empty_string(entry.get(key))]
        if missing:
            errors.append(f"{label}: missing or empty {', '.join(missing)}")
            continue
        kind = entry["kind"]
        status = entry["status"]
        if kind not in LEDGER_KINDS:
            errors.append(f"{label}: kind '{kind}' must be one of {', '.join(LEDGER_KINDS)}")
            continue
        allowed = {"sheet": SHEET_STATUSES, "probe": PROBE_STATUSES, "source": SOURCE_STATUSES}[kind]
        if status not in allowed:
            errors.append(f"{label} ({kind} {entry['source']}): status '{status}' must be one of {', '.join(allowed)}")
        ids = entry.get("candidate_ids", [])
        if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
            errors.append(f"{label}: candidate_ids must be a list of strings")
        if kind == "sheet":
            if entry["source"] in sheets:
                errors.append(f"{label}: sheet '{entry['source']}' appears twice in the ledger")
            sheets[entry["source"]] = entry

    if not sheets:
        errors.append("coverage_ledger has no kind: sheet entries; every sheet in the set must be listed")
    sheet_count = data.get("sheet_count")
    if sheet_count is not None and sheet_count != len(sheets):
        errors.append(f"sheet_count is {sheet_count} but the ledger lists {len(sheets)} sheets")

    seen_ids: set[str] = set()
    for index, candidate in enumerate(data["candidates"]):
        label = f"candidates[{index}]"
        if not isinstance(candidate, dict):
            errors.append(f"{label}: must be an object")
            continue
        missing = [key for key in CANDIDATE_REQUIRED if not non_empty_string(candidate.get(key))]
        cid = candidate.get("id")
        if non_empty_string(cid):
            label = cid
            if cid in seen_ids:
                errors.append(f"{label}: duplicate candidate id")
            seen_ids.add(cid)
        if missing:
            errors.append(f"{label}: missing or empty {', '.join(missing)}")
            continue

        division = candidate["division"]
        if division not in DIVISIONS:
            errors.append(f"{label}: division '{division}' is not a MasterFormat division that carries work")
        support = candidate["support_level"]
        if support not in SUPPORT_LEVELS:
            errors.append(f"{label}: support_level '{support}' must be one of {', '.join(SUPPORT_LEVELS)}")
        decision = candidate["decision"]
        if decision not in DECISIONS:
            errors.append(f"{label}: decision '{decision}' must be one of {', '.join(DECISIONS)}")
        if decision == "include" and support in NEVER_INCLUDE:
            errors.append(f"{label}: support_level '{support}' cannot be decision 'include'; use review or exclude")
        if support == "inferred" and decision != "review":
            errors.append(f"{label}: inferred candidates must be decision 'review'")
        if support == "spec_requirement" and not non_empty_string(candidate.get("spec_section")):
            errors.append(f"{label}: spec_requirement candidates must name spec_section")
        if candidate["sheet_number"] not in sheets:
            errors.append(f"{label}: sheet_number '{candidate['sheet_number']}' is not a sheet in the coverage ledger")
        for related in candidate.get("related_sheets", []) or []:
            if related not in sheets:
                errors.append(f"{label}: related sheet '{related}' is not a sheet in the coverage ledger")

    for index, entry in enumerate(data["coverage_ledger"]):
        if isinstance(entry, dict):
            for cid in entry.get("candidate_ids", []) or []:
                if isinstance(cid, str) and cid not in seen_ids:
                    errors.append(f"coverage_ledger[{index}] ({entry.get('source')}): candidate id '{cid}' does not exist")

    for list_name in ("assumptions", "exclusions", "rfis"):
        notes = data.get(list_name, [])
        if not isinstance(notes, list):
            errors.append(f"{list_name} must be a list")
            continue
        for index, note in enumerate(notes):
            label = f"{list_name}[{index}]"
            if not isinstance(note, dict):
                errors.append(f"{label}: must be an object")
                continue
            missing = [key for key in NOTE_REQUIRED if not non_empty_string(note.get(key))]
            if missing:
                errors.append(f"{label}: missing or empty {', '.join(missing)}")
            for cid in note.get("candidate_ids", []) or []:
                if cid not in seen_ids:
                    errors.append(f"{label}: candidate id '{cid}' does not exist")

    return errors


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------


def division_heading(division: str, level: int = 3) -> str:
    return f"{'#' * level} Division {division}: {DIVISIONS[division]}"


def cite(candidate: dict) -> str:
    sheets = candidate["sheet_number"]
    related = candidate.get("related_sheets") or []
    if related:
        sheets += ", also " + ", ".join(related)
    return f'{sheets}, {candidate["location"]}: "{candidate["quote"]}"'


def candidate_line(candidate: dict, with_reason: bool) -> list[str]:
    lines = [
        f"- **{candidate['candidate']}** ({candidate['support_level']}) "
        f"[{candidate['id']}]",
        f"  Source: {cite(candidate)}",
    ]
    if candidate.get("spec_section"):
        lines.append(f"  Spec: {candidate['spec_section']}")
    if with_reason:
        lines.append(f"  Reason: {candidate['reason']}")
    if candidate.get("notes"):
        lines.append(f"  Note: {candidate['notes']}")
    if candidate.get("cost_code"):
        lines.append(f"  Cost code: {candidate['cost_code']}")
    return lines


def by_division(candidates: list[dict]) -> list[tuple[str, list[dict]]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for candidate in candidates:
        grouped[candidate["division"]].append(candidate)
    return sorted(grouped.items())


def render_note(note: dict) -> str:
    line = f"- {note['text']} (Source: {note['source']})"
    ids = note.get("candidate_ids") or []
    if ids:
        line += f" [{', '.join(ids)}]"
    return line


def md_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def render(data: dict) -> str:
    candidates = data["candidates"]
    ledger = data["coverage_ledger"]
    included = [c for c in candidates if c["decision"] == "include"]
    review = [c for c in candidates if c["decision"] == "review"]
    excluded = [c for c in candidates if c["decision"] == "exclude"]
    sheets = [e for e in ledger if e["kind"] == "sheet"]
    others = [e for e in ledger if e["kind"] != "sheet"]

    status_counts = {status: 0 for status in SHEET_STATUSES}
    for sheet in sheets:
        status_counts[sheet["status"]] += 1
    reviewed = status_counts["reviewed"] + status_counts["reviewed_ocr"]

    out: list[str] = []
    out.append(f"# Scope list: {data['set_name']}")
    out.append("")
    out.append(
        f"{len(candidates)} candidates recorded: {len(included)} included, "
        f"{len(review)} for review, {len(excluded)} excluded. "
        f"Sheets: {reviewed} of {len(sheets)} reviewed"
        f" ({status_counts['reviewed_ocr']} via OCR, "
        f"{status_counts['unreadable']} unreadable, "
        f"{status_counts['not_reviewed']} not reviewed)."
    )
    out.append("")
    out.append(
        "Drawing-backed scope only. No quantities or pricing. Each item cites the "
        "sheet and the place on the sheet it came from. This is a draft for "
        "review against the full contract documents, not a takeoff or an estimate."
    )
    out.append("")

    out.append("## Included scope")
    out.append("")
    if not included:
        out.append("No candidates were included.")
        out.append("")
    for division, items in by_division(included):
        out.append(division_heading(division))
        out.append("")
        for item in items:
            out.extend(candidate_line(item, with_reason=False))
        out.append("")

    out.append("## Assumptions")
    out.append("")
    assumptions = data.get("assumptions") or []
    if assumptions:
        out.extend(render_note(note) for note in assumptions)
    else:
        out.append("None recorded.")
    out.append("")

    out.append("## Exclusions (by others)")
    out.append("")
    exclusions = data.get("exclusions") or []
    if not excluded and not exclusions:
        out.append("None recorded.")
        out.append("")
    if exclusions:
        out.extend(render_note(note) for note in exclusions)
        out.append("")
    for division, items in by_division(excluded):
        out.append(division_heading(division))
        out.append("")
        for item in items:
            out.extend(candidate_line(item, with_reason=True))
        out.append("")

    out.append("## RFIs / review items")
    out.append("")
    rfis = data.get("rfis") or []
    if not rfis and not review:
        out.append("None recorded.")
        out.append("")
    if rfis:
        out.append("### RFIs")
        out.append("")
        out.extend(render_note(note) for note in rfis)
        out.append("")
    if review:
        out.append("### Review items")
        out.append("")
        out.append(
            "Drawing-backed but unresolved. Each stays off the included list until "
            "the question in its reason is answered."
        )
        out.append("")
        for division, items in by_division(review):
            out.append(division_heading(division, level=4))
            out.append("")
            for item in items:
                out.extend(candidate_line(item, with_reason=True))
            out.append("")

    out.append("## Coverage ledger")
    out.append("")
    out.append("### Sheets")
    out.append("")
    out.append("| Sheet | Title | Status | Candidates | Note |")
    out.append("|---|---|---|---|---|")
    for sheet in sheets:
        ids = ", ".join(sheet.get("candidate_ids") or []) or "none"
        out.append(
            f"| {md_cell(sheet['source'])} | {md_cell(sheet.get('title', ''))} | "
            f"{sheet['status']} | {ids} | {md_cell(sheet['reason'])} |"
        )
    out.append("")
    if others:
        out.append("### Probes and other sources")
        out.append("")
        out.append("| Source | Kind | Status | Candidates | Note |")
        out.append("|---|---|---|---|---|")
        for entry in others:
            ids = ", ".join(entry.get("candidate_ids") or []) or "none"
            out.append(
                f"| {md_cell(entry['source'])} | {entry['kind']} | {entry['status']} | "
                f"{ids} | {md_cell(entry['reason'])} |"
            )
        out.append("")

    return "\n".join(out).rstrip() + "\n"


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    if len(argv) != 1 or argv[0] in ("-h", "--help"):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    data = load(Path(argv[0]))
    errors = validate(data)
    if errors:
        fail(errors)
    sys.stdout.write(render(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
