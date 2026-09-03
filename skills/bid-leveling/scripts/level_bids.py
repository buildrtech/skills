#!/usr/bin/env python3
"""Level subcontractor bid extractions into a comparison matrix.

Usage:
    python3 scripts/level_bids.py samples/*.json
    python3 scripts/level_bids.py bids/*.json decisions.json --xlsx leveled.xlsx

Every positional argument is a JSON file. The script tells them apart by
their top-level keys:

  - an extraction: one bidder's bid in the schema described in
    references/extraction-schema.md (has "bidder_name")
  - a merged file: {"submissions": [extraction, ...]}
  - estimator decisions: {"plugs": [...], "adjustments": [...]}

The leveled comparison is printed to stdout as Markdown. With --xlsx PATH the
same tables are also written to a workbook, which needs the optional openpyxl
package. Everything else is standard library.

The script never invents an amount. Plugs and adjustments come only from the
decisions file, and every gap without a plug is reported as unresolved.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_KEYS = (
    "bidder_name",
    "source_files",
    "document_role",
    "trade_scope",
    "total_bid_amount_in_cents",
    "scopes_of_work",
    "excluded_scopes",
    "alternate_lines",
    "unit_price_lines",
    "priced_qualifications",
    "review_items",
    "qualifications",
    "evidence",
)
LIST_KEYS = (
    "source_files",
    "scopes_of_work",
    "excluded_scopes",
    "alternate_lines",
    "unit_price_lines",
    "priced_qualifications",
    "review_items",
    "qualifications",
    "evidence",
)
INCLUDED_STATUSES = ("included",)
GAP_STATUSES = ("excluded", "omitted", "unknown")
ROW_CLASSES = ("base", "outside_scope", "supplier_or_installer", "review")
ALTERNATE_KINDS = ("add", "deduct", "replace")
NOT_ADDRESSED = "not_addressed"

STATUS_LABELS = {
    "included": "Included",
    "excluded": "Excluded",
    "omitted": "Omitted (silent)",
    "unknown": "Unknown",
    NOT_ADDRESSED: "Not addressed",
}
ROW_CLASS_TITLES = {
    "outside_scope": "Outside package scope",
    "supplier_or_installer": "Supplier and installer splits",
    "review": "Review rows",
}


# --------------------------------------------------------------------------
# Loading and validation
# --------------------------------------------------------------------------


def load_inputs(paths: list[str]) -> tuple[list[dict], dict, list[str]]:
    """Return (extractions, decisions, errors)."""
    extractions: list[dict] = []
    decisions: dict = {"plugs": [], "adjustments": []}
    errors: list[str] = []
    for raw_path in paths:
        path = Path(raw_path)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append(f"{path.name}: cannot read JSON ({exc})")
            continue
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and "submissions" in data:
            items = data.get("submissions") or []
        elif isinstance(data, dict) and ("plugs" in data or "adjustments" in data):
            decisions["plugs"].extend(data.get("plugs") or [])
            decisions["adjustments"].extend(data.get("adjustments") or [])
            for item in decisions["plugs"] + decisions["adjustments"]:
                item.setdefault("_file", path.name)
            continue
        elif isinstance(data, dict):
            items = [data]
        else:
            errors.append(f"{path.name}: top level must be an object or array")
            continue
        for item in items:
            if not isinstance(item, dict):
                errors.append(f"{path.name}: every submission must be an object")
                continue
            item["_file"] = path.name
            extractions.append(item)
    return extractions, decisions, errors


def _is_cents(value) -> bool:
    return value is None or (isinstance(value, int) and not isinstance(value, bool))


def validate_extraction(extraction: dict) -> list[str]:
    errors: list[str] = []
    label = extraction.get("_file", "extraction")
    missing = [key for key in REQUIRED_KEYS if key not in extraction]
    if missing:
        errors.append(f"{label}: missing required keys: {', '.join(missing)}")
        return errors
    if not isinstance(extraction["bidder_name"], str) or not extraction["bidder_name"].strip():
        errors.append(f"{label}: bidder_name must be a non-empty string")
    for key in LIST_KEYS:
        if not isinstance(extraction[key], list):
            errors.append(f"{label}: {key} must be a list (use [] when empty)")
    if errors:
        return errors
    if not _is_cents(extraction["total_bid_amount_in_cents"]):
        errors.append(f"{label}: total_bid_amount_in_cents must be an integer or null")
    for source in ("scopes_of_work", "excluded_scopes"):
        for index, entry in enumerate(extraction[source]):
            where = f"{label}: {source}[{index}]"
            if not isinstance(entry, dict):
                errors.append(f"{where} must be an object")
                continue
            if not entry.get("scope_key"):
                errors.append(f"{where} needs a scope_key")
            status = entry.get("status", "included" if source == "scopes_of_work" else None)
            allowed = INCLUDED_STATUSES if source == "scopes_of_work" else GAP_STATUSES
            if status not in allowed:
                errors.append(f"{where} status must be one of {', '.join(allowed)}")
            row_class = entry.get("row_class", "base")
            if row_class not in ROW_CLASSES:
                errors.append(f"{where} row_class must be one of {', '.join(ROW_CLASSES)}")
            if not _is_cents(entry.get("amount_in_cents")):
                errors.append(f"{where} amount_in_cents must be an integer or null")
    for index, entry in enumerate(extraction["alternate_lines"]):
        where = f"{label}: alternate_lines[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{where} must be an object")
            continue
        if not entry.get("alternate_key"):
            errors.append(f"{where} needs an alternate_key")
        if entry.get("kind") not in ALTERNATE_KINDS:
            errors.append(f"{where} kind must be one of {', '.join(ALTERNATE_KINDS)}")
        if not isinstance(entry.get("solicited"), bool):
            errors.append(f"{where} solicited must be true or false")
        if not _is_cents(entry.get("amount_in_cents")):
            errors.append(f"{where} amount_in_cents must be an integer or null")
    for index, entry in enumerate(extraction["unit_price_lines"]):
        if not isinstance(entry, dict) or not _is_cents(entry.get("unit_price_in_cents")):
            errors.append(f"{label}: unit_price_lines[{index}] needs an integer or null unit_price_in_cents")
    for index, entry in enumerate(extraction["priced_qualifications"]):
        if not isinstance(entry, dict) or not _is_cents(entry.get("amount_in_cents")):
            errors.append(f"{label}: priced_qualifications[{index}] needs an integer or null amount_in_cents")
        elif "in_total" in entry and not isinstance(entry["in_total"], bool):
            errors.append(f"{label}: priced_qualifications[{index}] in_total must be true or false")
    refs = {item.get("ref") for item in extraction["evidence"] if isinstance(item, dict)}
    for source in ("scopes_of_work", "excluded_scopes", "alternate_lines", "unit_price_lines", "priced_qualifications"):
        for index, entry in enumerate(extraction[source]):
            if isinstance(entry, dict) and entry.get("evidence_ref") and entry["evidence_ref"] not in refs:
                errors.append(f"{label}: {source}[{index}] cites evidence_ref '{entry['evidence_ref']}' that is not in evidence[]")
    return errors


def validate_decisions(decisions: dict, bidders: dict, rows: dict) -> list[str]:
    errors: list[str] = []
    for index, plug in enumerate(decisions["plugs"]):
        where = f"{plug.get('_file', 'decisions')}: plugs[{index}]"
        if plug.get("bidder_name") not in bidders:
            errors.append(f"{where} names unknown bidder '{plug.get('bidder_name')}'")
        if plug.get("scope_key") not in rows:
            errors.append(f"{where} names unknown scope_key '{plug.get('scope_key')}'")
        if not _is_cents(plug.get("amount_in_cents")) or plug.get("amount_in_cents") is None:
            errors.append(f"{where} amount_in_cents must be an integer")
        if not plug.get("source"):
            errors.append(f"{where} needs a source (who decided the amount and from what)")
    for index, adjustment in enumerate(decisions["adjustments"]):
        where = f"{adjustment.get('_file', 'decisions')}: adjustments[{index}]"
        if adjustment.get("bidder_name") not in bidders:
            errors.append(f"{where} names unknown bidder '{adjustment.get('bidder_name')}'")
        if not _is_cents(adjustment.get("amount_in_cents")) or adjustment.get("amount_in_cents") is None:
            errors.append(f"{where} amount_in_cents must be a signed integer")
        if not adjustment.get("description") or not adjustment.get("source"):
            errors.append(f"{where} needs a description and a source")
    return errors


# --------------------------------------------------------------------------
# Model
# --------------------------------------------------------------------------


def build_model(extractions: list[dict], decisions: dict) -> dict:
    bidders: dict[str, dict] = {}
    rows: dict[str, dict] = {}
    flags: list[str] = []

    for extraction in extractions:
        name = extraction["bidder_name"].strip()
        if name in bidders:
            flags.append(
                f"{name}: appears in more than one extraction ({bidders[name]['file']} and "
                f"{extraction['_file']}); only the first was used. Merge revised bids into one extraction."
            )
            continue
        bidders[name] = {
            "name": name,
            "file": extraction["_file"],
            "extraction": extraction,
            "total": extraction["total_bid_amount_in_cents"],
            "plugs": [],
            "adjustments": [],
        }
        for source in ("scopes_of_work", "excluded_scopes"):
            for entry in extraction[source]:
                key = entry["scope_key"]
                status = entry.get("status", "included" if source == "scopes_of_work" else "excluded")
                row = rows.setdefault(
                    key,
                    {
                        "key": key,
                        "label": entry.get("scope") or key,
                        "row_class": entry.get("row_class", "base"),
                        "cells": {},
                    },
                )
                if entry.get("row_class", "base") != row["row_class"]:
                    flags.append(
                        f"{name}: row '{key}' classified as {entry.get('row_class', 'base')} but an earlier "
                        f"bidder classified it as {row['row_class']}; the first classification was kept."
                    )
                if key in row["cells"]:
                    flags.append(f"{name}: row '{key}' appears twice in the extraction; the first entry was kept.")
                    continue
                row["cells"][name] = {
                    "status": status,
                    "amount": entry.get("amount_in_cents"),
                    "note": entry.get("note"),
                    "evidence_ref": entry.get("evidence_ref"),
                    "plug": None,
                }

    for row in rows.values():
        for name in bidders:
            if name not in row["cells"]:
                row["cells"][name] = {"status": NOT_ADDRESSED, "amount": None, "note": None, "evidence_ref": None, "plug": None}
                if row["row_class"] == "base":
                    flags.append(
                        f"{name}: base row '{row['label']}' is not in the extraction at all. Re-read the bid and "
                        "record it as included, excluded, omitted, or unknown."
                    )

    for plug in decisions["plugs"]:
        name, key = plug.get("bidder_name"), plug.get("scope_key")
        if name not in bidders or key not in rows:
            continue
        cell = rows[key]["cells"][name]
        if rows[key]["row_class"] != "base":
            flags.append(f"{name}: plug on '{rows[key]['label']}' ignored because the row is {rows[key]['row_class']}, not base.")
            continue
        if cell["status"] in INCLUDED_STATUSES:
            flags.append(f"{name}: plug on '{rows[key]['label']}' ignored because the bidder already includes that scope.")
            continue
        cell["plug"] = plug
        bidders[name]["plugs"].append({"row": rows[key], "plug": plug})

    for adjustment in decisions["adjustments"]:
        name = adjustment.get("bidder_name")
        if name in bidders:
            bidders[name]["adjustments"].append(adjustment)

    for bidder in bidders.values():
        gaps = [
            row for row in rows.values()
            if row["row_class"] == "base"
            and row["cells"][bidder["name"]]["status"] not in INCLUDED_STATUSES
            and row["cells"][bidder["name"]]["plug"] is None
        ]
        bidder["unresolved"] = gaps
        plug_total = sum(item["plug"]["amount_in_cents"] for item in bidder["plugs"])
        adjustment_total = sum(item["amount_in_cents"] for item in bidder["adjustments"])
        bidder["plug_total"] = plug_total
        bidder["adjustment_total"] = adjustment_total
        bidder["leveled"] = None if bidder["total"] is None else bidder["total"] + plug_total + adjustment_total
        bidder["complete"] = bidder["total"] is not None and not gaps
        if bidder["total"] is None:
            flags.append(f"{bidder['name']}: no total_bid_amount_in_cents; leveled total cannot be computed.")

        included = [
            entry for entry in bidder["extraction"]["scopes_of_work"]
            if entry.get("status", "included") in INCLUDED_STATUSES
        ]
        amounts = [entry.get("amount_in_cents") for entry in included]
        in_total = [
            entry["amount_in_cents"] for entry in bidder["extraction"]["priced_qualifications"]
            if entry.get("in_total") is True and entry.get("amount_in_cents") is not None
        ]
        if included and all(amount is not None for amount in amounts) and bidder["total"] is not None:
            itemized = sum(amounts) + sum(in_total)
            if itemized != bidder["total"]:
                flags.append(
                    f"{bidder['name']}: itemized lines (plus priced qualifications marked in_total) sum to "
                    f"{money(itemized)} but the stated total is {money(bidder['total'])} "
                    f"(difference {money(itemized - bidder['total'])}). Confirm with the bidder."
                )

    trades = {bidder["extraction"]["trade_scope"] for bidder in bidders.values()}
    if len(trades) > 1:
        flags.append(f"Extractions name different trade scopes ({', '.join(sorted(str(t) for t in trades))}); confirm they belong in one package.")

    return {"bidders": bidders, "rows": rows, "flags": flags, "trade": next(iter(trades), None) if trades else None}


# --------------------------------------------------------------------------
# Formatting helpers
# --------------------------------------------------------------------------


def money(cents) -> str:
    if cents is None:
        return "n/a"
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    dollars, remainder = divmod(cents, 100)
    if remainder:
        return f"{sign}${dollars:,}.{remainder:02d}"
    return f"{sign}${dollars:,}"


def cell_text(cell: dict) -> str:
    text = STATUS_LABELS.get(cell["status"], cell["status"])
    if cell["status"] in INCLUDED_STATUSES and cell["amount"] is not None:
        text += f" ({money(cell['amount'])})"
    if cell["plug"] is not None:
        text += f"; plug {money(cell['plug']['amount_in_cents'])}"
    return text


def md_escape(value) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ")


def md_table(headers: list[str], rows: list[list]) -> list[str]:
    lines = ["| " + " | ".join(md_escape(h) for h in headers) + " |", "|" + "---|" * len(headers)]
    for row in rows:
        lines.append("| " + " | ".join(md_escape(c) for c in row) + " |")
    return lines


# --------------------------------------------------------------------------
# Tables (shared by Markdown and XLSX)
# --------------------------------------------------------------------------


def summary_table(model: dict) -> tuple[list[str], list[list]]:
    headers = ["Bidder", "Base bid", "Plugs", "Adjustments", "Leveled total", "Unresolved gaps", "Documents"]
    rows = []
    for bidder in model["bidders"].values():
        leveled = money(bidder["leveled"])
        if bidder["leveled"] is not None and not bidder["complete"]:
            leveled += " (incomplete)"
        rows.append([
            bidder["name"],
            money(bidder["total"]),
            money(bidder["plug_total"]) if bidder["plugs"] else "none",
            money(bidder["adjustment_total"]) if bidder["adjustments"] else "none",
            leveled,
            str(len(bidder["unresolved"])),
            ", ".join(bidder["extraction"]["source_files"]) or "not stated",
        ])
    return headers, rows


def matrix_table(model: dict, row_class: str) -> tuple[list[str], list[list]]:
    names = list(model["bidders"])
    headers = ["Scope"] + names
    rows = []
    for row in model["rows"].values():
        if row["row_class"] != row_class:
            continue
        rows.append([row["label"]] + [cell_text(row["cells"][name]) for name in names])
    return headers, rows


def gaps_table(model: dict) -> tuple[list[str], list[list]]:
    headers = ["Scope", "Bidder", "Bid says", "Plug", "Plug source", "Evidence"]
    rows = []
    for row in model["rows"].values():
        if row["row_class"] != "base":
            continue
        for name, cell in row["cells"].items():
            if cell["status"] in INCLUDED_STATUSES:
                continue
            said = STATUS_LABELS.get(cell["status"], cell["status"])
            if cell["note"]:
                said += f": {cell['note']}"
            plug = cell["plug"]
            rows.append([
                row["label"],
                name,
                said,
                money(plug["amount_in_cents"]) if plug else "none: unresolved",
                plug.get("source", "") if plug else "",
                cell["evidence_ref"] or "",
            ])
    return headers, rows


def adjustments_table(model: dict) -> tuple[list[str], list[list]]:
    headers = ["Bidder", "Adjustment", "Amount", "Source"]
    rows = []
    for bidder in model["bidders"].values():
        for adjustment in bidder["adjustments"]:
            rows.append([bidder["name"], adjustment["description"], money(adjustment["amount_in_cents"]), adjustment["source"]])
    return headers, rows


def alternates_table(model: dict) -> tuple[list[str], list[list]]:
    names = list(model["bidders"])
    headers = ["Alternate", "Kind", "Solicited"] + names
    alternates: dict[str, dict] = {}
    for name, bidder in model["bidders"].items():
        for entry in bidder["extraction"]["alternate_lines"]:
            key = entry["alternate_key"]
            alt = alternates.setdefault(key, {"label": entry.get("label") or key, "kind": entry["kind"], "solicited": entry["solicited"], "cells": {}})
            amount = money(entry["amount_in_cents"]) if entry.get("amount_in_cents") is not None else "priced: not stated"
            alt["cells"][name] = amount
    rows = []
    for alt in alternates.values():
        rows.append([alt["label"], alt["kind"], "yes" if alt["solicited"] else "no (bidder-proposed)"] + [alt["cells"].get(name, "not offered") for name in names])
    return headers, rows


def unit_prices_table(model: dict) -> tuple[list[str], list[list]]:
    headers = ["Bidder", "Unit price line", "Unit", "Unit price", "Quantity", "Evidence"]
    rows = []
    for name, bidder in model["bidders"].items():
        for entry in bidder["extraction"]["unit_price_lines"]:
            quantity = entry.get("quantity")
            rows.append([
                name,
                entry.get("description", ""),
                entry.get("unit", ""),
                money(entry.get("unit_price_in_cents")),
                "" if quantity is None else str(quantity),
                entry.get("evidence_ref", "") or "",
            ])
    return headers, rows


def qualifications_table(model: dict) -> tuple[list[str], list[list]]:
    headers = ["Bidder", "Priced qualification", "Amount", "In bid total?", "Evidence"]
    rows = []
    for name, bidder in model["bidders"].items():
        for entry in bidder["extraction"]["priced_qualifications"]:
            rows.append([
                name,
                entry.get("description", ""),
                money(entry.get("amount_in_cents")) if entry.get("amount_in_cents") is not None else "not stated",
                "yes" if entry.get("in_total") is True else "no",
                entry.get("evidence_ref", "") or "",
            ])
    return headers, rows


def evidence_table(model: dict) -> tuple[list[str], list[list]]:
    headers = ["Bidder", "Ref", "Source file", "Location", "Quote"]
    rows = []
    for name, bidder in model["bidders"].items():
        for item in bidder["extraction"]["evidence"]:
            rows.append([name, item.get("ref", ""), item.get("source_file", ""), item.get("location", ""), item.get("quote", "")])
    return headers, rows


# --------------------------------------------------------------------------
# Markdown
# --------------------------------------------------------------------------


def _text_items(entry) -> str:
    if isinstance(entry, dict):
        text = entry.get("description") or entry.get("text") or ""
        ref = entry.get("evidence_ref")
        return f"{text} ({ref})" if ref else text
    return str(entry)


def render_markdown(model: dict, title: str | None) -> str:
    bidders = model["bidders"]
    out: list[str] = []
    out.append(f"# Leveled bid comparison: {title or model['trade'] or 'untitled package'}")
    out.append("")

    complete = [b for b in bidders.values() if b["complete"]]
    incomplete = [b for b in bidders.values() if not b["complete"]]
    if complete:
        low = min(complete, key=lambda b: b["leveled"])
        out.append(f"**Lowest complete leveled total:** {low['name']} at {money(low['leveled'])}.")
    else:
        out.append("**Lowest complete leveled total:** none; every bidder still has unresolved gaps or no stated total.")
    for bidder in incomplete:
        count = len(bidder["unresolved"])
        if bidder["leveled"] is None:
            out.append(f"**{bidder['name']}:** no stated total, so no leveled total.")
        else:
            gap_labels = "; ".join(row["label"] for row in bidder["unresolved"])
            out.append(
                f"**{bidder['name']}:** {money(bidder['leveled'])} before {count} unresolved gap{'s' if count != 1 else ''} ({gap_labels})."
            )
    out.append("")
    out.append("Leveled total = base bid + plugs + adjustments. Alternates, unit prices, and priced qualifications are listed but not applied. Every plug and adjustment below names its source; nothing was estimated by this script.")
    out.append("")

    out.append("## Summary")
    out.append("")
    out.extend(md_table(*summary_table(model)))
    out.append("")

    out.append("## Base scope matrix")
    out.append("")
    headers, rows = matrix_table(model, "base")
    out.extend(md_table(headers, rows) if rows else ["No base rows were extracted."])
    out.append("")

    out.append("## Scope gaps and plugs")
    out.append("")
    headers, rows = gaps_table(model)
    if rows:
        out.extend(md_table(headers, rows))
        unresolved = sum(1 for row in rows if row[3].startswith("none"))
        out.append("")
        out.append(f"{len(rows)} gap{'s' if len(rows) != 1 else ''} on base scope, {unresolved} unresolved. An unresolved gap keeps that bidder's leveled total incomplete.")
    else:
        out.append("No gaps: every bidder includes every base row.")
    out.append("")

    headers, rows = adjustments_table(model)
    if rows:
        out.append("## Adjustments")
        out.append("")
        out.extend(md_table(headers, rows))
        out.append("")

    out.append("## Alternates")
    out.append("")
    headers, rows = alternates_table(model)
    if rows:
        out.extend(md_table(headers, rows))
        out.append("")
        out.append("Alternates are not in the leveled totals. Bidder-proposed alternates need a review decision before they count for anything.")
    else:
        out.append("No alternates were extracted.")
    out.append("")

    headers, rows = unit_prices_table(model)
    if rows:
        out.append("## Unit prices")
        out.append("")
        out.extend(md_table(headers, rows))
        out.append("")

    headers, rows = qualifications_table(model)
    if rows:
        out.append("## Priced qualifications (not applied)")
        out.append("")
        out.extend(md_table(headers, rows))
        out.append("")
        out.append("Bonds, taxes, escalation, and similar items stay here until the estimator decides whether every bid should carry them on the same basis.")
        out.append("")

    for row_class, section_title in ROW_CLASS_TITLES.items():
        headers, rows = matrix_table(model, row_class)
        if rows:
            out.append(f"## {section_title}")
            out.append("")
            out.extend(md_table(headers, rows))
            out.append("")
            if row_class == "outside_scope":
                out.append("Amounts here are inside the bidder's total but outside this package. Remove them with a sourced adjustment, not by editing the bid.")
                out.append("")

    out.append("## Review items")
    out.append("")
    review_lines: list[str] = []
    for name, bidder in bidders.items():
        for entry in bidder["extraction"]["review_items"]:
            review_lines.append(f"- {name}: {_text_items(entry)}")
    for flag in model["flags"]:
        review_lines.append(f"- Leveling check: {flag}")
    out.extend(review_lines or ["- None."])
    out.append("")

    out.append("## Qualifications")
    out.append("")
    any_qualification = False
    for name, bidder in bidders.items():
        qualifications = bidder["extraction"]["qualifications"]
        if not qualifications:
            continue
        any_qualification = True
        out.append(f"**{name}**")
        out.append("")
        for entry in qualifications:
            out.append(f"- {_text_items(entry)}")
        out.append("")
    if not any_qualification:
        out.append("None extracted.")
        out.append("")

    out.append("## Evidence")
    out.append("")
    headers, rows = evidence_table(model)
    out.extend(md_table(headers, rows) if rows else ["No evidence entries were extracted."])
    out.append("")

    out.append("## Basis")
    out.append("")
    out.append("- Bidders and amounts come only from the extraction files listed in the Summary table; the script adds nothing.")
    out.append("- Each bidder's base bid stays at the submission level. Itemized amounts, where a bid gives them, are shown but never spread across rows.")
    out.append("- Plugs are estimator decisions recorded in the decisions file. They level a bidder's gap for comparison and are not the bidder's price.")
    out.append("- This is arithmetic on extracted evidence, not an award recommendation and not a scope review.")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# XLSX
# --------------------------------------------------------------------------


def write_xlsx(model: dict, path: Path, title: str | None) -> None:
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font
    except ImportError:
        raise SystemExit(
            f"Markdown was printed, but {path} was not written: openpyxl is not installed. "
            "Install it with 'python3 -m pip install openpyxl' and rerun, or use the Markdown output."
        )

    workbook = Workbook()
    sheets = [
        ("Summary", summary_table(model)),
        ("Base scope matrix", matrix_table(model, "base")),
        ("Gaps and plugs", gaps_table(model)),
        ("Adjustments", adjustments_table(model)),
        ("Alternates", alternates_table(model)),
        ("Unit prices", unit_prices_table(model)),
        ("Priced qualifications", qualifications_table(model)),
    ]
    for row_class, section_title in ROW_CLASS_TITLES.items():
        sheets.append((section_title[:31], matrix_table(model, row_class)))
    review_rows = [[name, _text_items(entry)] for name, b in model["bidders"].items() for entry in b["extraction"]["review_items"]]
    review_rows += [["Leveling check", flag] for flag in model["flags"]]
    sheets.append(("Review items", (["Bidder", "Item"], review_rows)))
    qualification_rows = [[name, _text_items(entry)] for name, b in model["bidders"].items() for entry in b["extraction"]["qualifications"]]
    sheets.append(("Qualifications", (["Bidder", "Qualification"], qualification_rows)))
    sheets.append(("Evidence", evidence_table(model)))

    first = True
    for sheet_name, (headers, rows) in sheets:
        if not rows and sheet_name not in ("Summary", "Base scope matrix"):
            continue
        sheet = workbook.active if first else workbook.create_sheet()
        first = False
        sheet.title = sheet_name
        if sheet_name == "Summary":
            sheet.append([f"Leveled bid comparison: {title or model['trade'] or 'untitled package'}"])
            sheet.append(["Leveled total = base bid + plugs + adjustments. Alternates, unit prices, and priced qualifications are not applied."])
            sheet.append([])
        sheet.append(headers)
        for cell in sheet[sheet.max_row]:
            cell.font = Font(bold=True)
        for row in rows:
            sheet.append(row)
        for column in sheet.columns:
            width = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column)
            sheet.column_dimensions[column[0].column_letter].width = min(max(12, width + 2), 60)
    workbook.save(path)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Level subcontractor bid extractions into a comparison matrix.")
    parser.add_argument("files", nargs="+", help="extraction JSON files, merged files, and an optional decisions file")
    parser.add_argument("--xlsx", metavar="PATH", help="also write the comparison as an .xlsx workbook (needs openpyxl)")
    parser.add_argument("--title", help="package title for the heading (defaults to the extracted trade_scope)")
    args = parser.parse_args(argv)

    extractions, decisions, errors = load_inputs(args.files)
    for extraction in extractions:
        errors.extend(validate_extraction(extraction))
    if not extractions and not errors:
        errors.append("no extractions found in the input files")
    if errors:
        print("Extraction validation failed. Fix the JSON, do not hand-edit the comparison:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 2

    model = build_model(extractions, decisions)
    decision_errors = validate_decisions(decisions, model["bidders"], model["rows"])
    if decision_errors:
        print("Decisions file validation failed:", file=sys.stderr)
        for error in decision_errors:
            print(f"  - {error}", file=sys.stderr)
        return 2

    sys.stdout.write(render_markdown(model, args.title))
    if args.xlsx:
        write_xlsx(model, Path(args.xlsx), args.title)
        print(f"Wrote {args.xlsx}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
