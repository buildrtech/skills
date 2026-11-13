#!/usr/bin/env python3
"""Level sub bids into one Excel bid tab: every scope item by bidder, plug cells, review flags.

    python3 level.py bid-data.json bid-tab.xlsx

Writes the workbook, then prints the leveled totals and what is flagged.
Standard library only, Python 3.8 or newer. Money in the JSON is dollars; the
script works in integer cents.
"""

import json
import math
import re
import sys
import zipfile
from collections import Counter
from io import BytesIO

STATUSES = ["included", "excluded", "omitted", "unclear"]
KEY = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

# Review flags, in the words the Review sheet shows.
NEEDS, SUGGESTED, ENTERED, ADDENDA, EXTRA, CHECK = "Needs a plug", "Suggested plug", "Your plug", "Addenda", "Not on scope sheet", "Check"


class BidDataError(ValueError):
    pass


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def cents(dollars):
    return int(math.floor(dollars * 100 + 0.5))


def is_money(v):
    return _is_number(v) and abs(v * 100 - round(v * 100)) < 1e-6


def is_text(v):
    return isinstance(v, str) and v.strip() != ""


def money(c):
    a = abs(c)
    text = "${:,}".format(a // 100) + (".{:02d}".format(a % 100) if a % 100 else "")
    return "-" + text if c < 0 else text


def validate(data):
    errors = []

    def need(ok, message):
        if not ok:
            errors.append(message)

    if not isinstance(data, dict):
        raise BidDataError("bid data has 1 problem:\n- the file must hold one JSON object")
    need(is_text(data.get("project")), "project is required")
    need(is_text(data.get("package")), "package is required")
    need(isinstance(data.get("asOf"), str) and re.match(r"^\d{4}-\d{2}-\d{2}$", data["asOf"]), "asOf must be YYYY-MM-DD")
    addenda = data.get("addenda")
    need(isinstance(addenda, list) and all(isinstance(n, int) and not isinstance(n, bool) and n > 0 for n in addenda),
         "addenda must be a list of addendum numbers ([] for none)")
    scope = data.get("scope") if isinstance(data.get("scope"), list) else []
    keys, extras = [], set()
    for row in scope:
        row = row if isinstance(row, dict) else {}
        key = row.get("key")
        need(isinstance(key, str) and KEY.match(key) and key not in keys,
             'scope key "{}" must be unique: lowercase letters, digits, - or _'.format(key))
        need(is_text(row.get("label")), 'scope line "{}" needs a label'.format(key))
        need(isinstance(row.get("extra", False), bool), 'scope line "{}": extra must be true or false'.format(key))
        keys.append(key)
        if row.get("extra") is True:
            extras.add(key)
    need(len(keys) > len(extras), "scope must list at least one scope line that isn't extra")
    bids = data.get("bids") if isinstance(data.get("bids"), list) else []
    need(len(bids) >= 2, "at least two bids are needed to level")
    bidders = set()
    for bid in bids:
        bid = bid if isinstance(bid, dict) else {}
        who = bid.get("bidder") or "(unnamed bid)"
        need(is_text(bid.get("bidder")) and bid.get("bidder") not in bidders, 'bidder "{}" must be named and unique'.format(who))
        bidders.add(bid.get("bidder"))
        need(is_text(bid.get("file")), "{}: file is required".format(who))
        need(is_money(bid.get("total")) and bid["total"] > 0, "{}: total must be the stated base bid in dollars".format(who))
        acked = bid.get("addenda", "missing")
        need(acked is None or (isinstance(acked, list) and all(isinstance(n, int) and not isinstance(n, bool) for n in acked)),
             "{}: addenda must list acknowledged addendum numbers, or be null when the bid doesn't say".format(who))
        notes = bid.get("notes")
        need(notes is None or (isinstance(notes, list) and all(is_text(t) for t in notes)), "{}: notes must be a list of text".format(who))
        review = bid.get("review")
        need(review is None or (isinstance(review, list) and all(
            isinstance(item, dict) and is_text(item.get("check")) and (item.get("ask") is None or is_text(item["ask"]))
            and (item.get("scope") is None or item["scope"] in keys) for item in review)),
            '{}: review must be a list of {{"check": what to look at, "ask": optional question for the bidder, '
            '"scope": optional key of the scope line it is about}}'.format(who))
        cells = bid.get("scope") if isinstance(bid.get("scope"), dict) else {}
        for key in keys:
            cell = cells.get(key)
            if not isinstance(cell, dict):
                errors.append('{}: no entry for scope line "{}" (use "omitted" if the bid doesn\'t mention it)'.format(who, key))
                continue
            status = cell.get("status")
            need(status in STATUSES, "{} / {}: status must be one of {}".format(who, key, ", ".join(STATUSES)))
            need(status == "omitted" or is_text(cell.get("quote")), "{} / {}: quote the bid's words".format(who, key))
            need("amount" not in cell or (status == "included" and is_money(cell["amount"])),
                 "{} / {}: only included lines carry an amount, in dollars".format(who, key))
        for key in cells:
            need(key in keys, '{}: "{}" is not a scope line'.format(who, key))
    plugs = data.get("plugs")
    need(plugs is None or isinstance(plugs, list), "plugs must be a list")
    plugged = set()
    for plug in plugs if isinstance(plugs, list) else []:
        plug = plug if isinstance(plug, dict) else {}
        bid = next((b for b in bids if isinstance(b, dict) and b.get("bidder") == plug.get("bidder")), None)
        where = "plug {} / {}".format(plug.get("bidder"), plug.get("scope"))
        need(bid is not None, '{}: no bid from "{}"'.format(where, plug.get("bidder")))
        need(plug.get("scope") in keys, "{}: not a scope line".format(where))
        if bid is not None and plug.get("scope") in keys and plug["scope"] not in extras:
            cell = (bid.get("scope") or {}).get(plug["scope"])
            need(isinstance(cell, dict) and cell.get("status") != "included",
                 "{}: the bid includes this line, so there is nothing to plug".format(where))
        need(is_money(plug.get("amount")), "{}: amount must be in dollars".format(where))
        need(is_text(plug.get("source")), "{}: say where the figure came from".format(where))
        need((plug.get("bidder"), plug.get("scope")) not in plugged, "{}: plugged twice".format(where))
        plugged.add((plug.get("bidder"), plug.get("scope")))
    if errors:
        raise BidDataError("bid data has {} problem{}:\n- {}".format(len(errors), "" if len(errors) == 1 else "s", "\n- ".join(errors)))
    return data


def suggest(data, bid, key):
    """The highest price another bidder itemized for the same line, or None."""
    best = None
    for other in data["bids"]:
        cell = other["scope"][key]
        if other is bid or cell["status"] != "included" or "amount" not in cell:
            continue
        if best is None or cents(cell["amount"]) > best["amount"]:
            best = {"amount": cents(cell["amount"]), "bidder": other["bidder"]}
    return best


def lower(label):
    # "Level 5 finish (Addendum 2)" reads as "level 5 finish (Addendum 2)" mid-sentence; acronyms stay.
    return label[0].lower() + label[1:] if re.match(r"^[A-Z][a-z]", label) else label


def said(quote):
    return 'Your bid says "{}"{}'.format(quote, "" if re.search(r"[.!?]$", quote) else ".")


QUESTION = {
    "excluded": lambda label, quote: "{} Confirm your bid excludes {}, or give us an add price.".format(said(quote), lower(label)),
    "omitted": lambda label, quote: "Your bid doesn't mention {}. Is it in your base bid? If not, what would you add?".format(lower(label)),
    "unclear": lambda label, quote: "{} Does your base bid include {}?".format(said(quote), lower(label)),
}

SAYS = {"included": "Included", "excluded": "Excluded", "omitted": "Not mentioned", "unclear": "Unclear"}


def says(cell, quote_included=False):
    """What the bid says about a line, as the workbook shows it."""
    if cell["status"] == "included" and not quote_included:
        return "Included" + (" " + money(cents(cell["amount"])) if "amount" in cell else "")
    return '{}: "{}"'.format(SAYS[cell["status"]], cell["quote"]) if cell.get("quote") else SAYS[cell["status"]]


def _addenda(numbers):
    return "Addend{} {}".format("um" if len(numbers) == 1 else "a", " and ".join(str(n) for n in numbers))


def level(data):
    """Each bid's plugs, leveled total, open gaps, rank, and review flags."""
    entered = {(p["bidder"], p["scope"]): p for p in data.get("plugs") or []}
    results = []
    for bid in data["bids"]:
        who, cells, review = bid["bidder"], [], []

        def flag(kind, why, ask="", row=None, said_text=""):
            review.append({"flag": kind, "bidder": who, "scope": row["label"] if row else "", "says": said_text, "why": why, "ask": ask})

        acked = bid.get("addenda")
        missing = [n for n in data["addenda"] if n not in acked] if acked is not None else []
        if acked is None and data["addenda"]:
            flag(ADDENDA, "The bid doesn't say which addenda its price covers.",
                 "Your bid doesn't say which addenda it covers. Confirm it includes {}.".format(_addenda(data["addenda"])))
        if missing:
            flag(ADDENDA, "The bid acknowledges {}, not {}.".format(_addenda(acked) if acked else "no addenda", _addenda(missing)),
                 "Your bid acknowledges {}. Confirm you received {} and that your price covers {}.".format(
                     _addenda(acked) if acked else "no addenda", _addenda(missing), "it" if len(missing) == 1 else "them"))
        for row in data["scope"]:
            cell = bid["scope"][row["key"]]
            status = cell["status"]
            plug = entered.get((who, row["key"]))
            item = {"row": row, "cell": cell, "gap": False, "suggested": False, "amount": cents(plug["amount"]) if plug else None}
            if row.get("extra"):
                # A line a bid raises that the scope sheet doesn't list: flagged, never a gap.
                if status != "omitted" or plug:
                    why = "The scope sheet doesn't list this line. Decide whether it belongs in this package."
                    if plug:
                        why += " Plug of {} entered. Source: {}.".format(money(item["amount"]), plug["source"])
                    elif status != "omitted":
                        why += " If it changes the comparison, enter a plug (negative to take it out of this bid)."
                    ask = "{} That isn't in this package. What would you deduct to take it out?".format(said(cell["quote"])) if status == "included" else ""
                    flag(EXTRA, why, ask, row, says(cell, quote_included=True))
            elif status != "included":
                item["gap"] = True
                suggestion = None if plug or status == "unclear" else suggest(data, bid, row["key"])
                if plug:
                    kind, why = ENTERED, "Plug of {} entered. Source: {}.".format(money(item["amount"]), plug["source"])
                elif suggestion:
                    item.update(amount=suggestion["amount"], suggested=True)
                    kind, why = SUGGESTED, "Plug of {} is the highest price another bidder itemized for this line ({}). Keep it or type your own.".format(
                        money(suggestion["amount"]), suggestion["bidder"])
                elif status == "unclear":
                    kind, why = NEEDS, "The wording doesn't settle whether this is in the price. The bid stays incomplete until you enter a plug."
                else:
                    kind, why = NEEDS, "No other bid itemizes this line, so there is no price to suggest. The bid stays incomplete until you enter a plug."
                flag(kind, why, QUESTION[status](row["label"], cell.get("quote")), row, says(cell))
            cells.append(item)
        for check in bid.get("review") or []:
            about = next((row for row in data["scope"] if row["key"] == check.get("scope")), None)
            flag(CHECK, check["check"], check.get("ask") or "", about, says(bid["scope"][about["key"]]) if about else "")
        base = cents(bid["total"])
        plugs = sum(c["amount"] or 0 for c in cells)
        results.append({"bid": bid, "base": base, "plugs": plugs, "leveled": base + plugs, "cells": cells, "review": review,
                        "missing": missing, "open": sum(1 for c in cells if c["gap"] and c["amount"] is None)})
    for r in results:
        r["complete"] = r["open"] == 0
        r["base_rank"] = 1 + sum(1 for o in results if o["base"] < r["base"])
        r["rank"] = 1 + sum(1 for o in results if o["open"] == 0 and o["leveled"] < r["leveled"]) if r["complete"] else None
    complete = [r for r in results if r["complete"]]
    return {"results": results, "lowest_base": min(results, key=lambda r: r["base"]),
            "lowest_complete": min(complete, key=lambda r: r["leveled"]) if complete else None}


# ---------- XLSX ----------

# Cell styles (indexes into cellXfs below) and conditional formats (indexes into dxfs).
PLAIN, BOLD, MONEY, MONEY_BOLD, WRAP, TITLE, HEAD, FLAG, INPUT, RIGHT = range(10)
DXF_OPEN, DXF_SUGGESTED, DXF_LOW = range(3)

STYLES = (
    '<numFmts count="1"><numFmt numFmtId="164" formatCode="&quot;$&quot;#,##0.00"/></numFmts>'
    '<fonts count="3"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font>'
    '<font><b/><sz val="14"/><name val="Calibri"/></font></fonts>'
    '<fills count="5"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>'
    + "".join('<fill><patternFill patternType="solid"><fgColor rgb="FF{}"/><bgColor indexed="64"/></patternFill></fill>'.format(rgb)
              for rgb in ("D9E1F2", "FCE4D6", "FFF2CC"))  # header blue-grey, flagged peach, input yellow
    + '</fills><borders count="2"><border/><border>'
    + "".join('<{0} style="thin"><color rgb="FFBFBFBF"/></{0}>'.format(side) for side in ("left", "right", "top", "bottom"))
    + '</border></borders><cellStyleXfs count="1"><xf/></cellStyleXfs><cellXfs count="10"><xf/>'
    '<xf fontId="1" applyFont="1" applyAlignment="1">{top}</xf><xf numFmtId="164" applyNumberFormat="1" applyAlignment="1">{top}</xf>'
    '<xf numFmtId="164" fontId="1" applyNumberFormat="1" applyFont="1" applyAlignment="1">{top}</xf>'
    '<xf applyAlignment="1">{wrap}</xf><xf fontId="2" applyFont="1"/>'
    '<xf fontId="1" fillId="2" applyFont="1" applyFill="1" applyAlignment="1">{wrap}</xf><xf fillId="3" applyFill="1" applyAlignment="1">{wrap}</xf>'
    '<xf numFmtId="164" fillId="4" borderId="1" applyNumberFormat="1" applyFill="1" applyBorder="1" applyAlignment="1">{top}</xf>'
    '<xf applyAlignment="1"><alignment horizontal="right" vertical="top"/></xf></cellXfs>'.format(
        top='<alignment vertical="top"/>', wrap='<alignment wrapText="1" vertical="top"/>')
    + '<dxfs count="3"><dxf><fill><patternFill><bgColor rgb="FFFFC7CE"/></patternFill></fill></dxf>'
    '<dxf><font><i/><color rgb="FFC65911"/></font></dxf>'
    '<dxf><font><b/></font><fill><patternFill><bgColor rgb="FFC6EFCE"/></patternFill></fill></dxf></dxfs>'
)

NOTES = (
    "Bids as of {asOf}. {addenda}. This is a comparison, not an award recommendation.",
    "Yellow = type a plug here. Red = still needs a plug. Orange italic = a suggested plug taken from another bid; type over it.",
    "Enter 0 when the bidder confirms the item is in their price. Every flag is on the Review sheet with a question for the bidder.",
)


def xml(v):
    text = "" if v is None else str(v)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    return re.sub("[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)


def col(i):
    s = ""
    n = i + 1
    while n > 0:
        s = chr(65 + (n - 1) % 26) + s
        n = (n - 1) // 26
    return s


def dollars(c):
    """Cents as the shortest decimal number: 80380000 -> 803800, 17550 -> 175.5."""
    return str(c // 100) if c % 100 == 0 else repr(c / 100)


def cell_xml(ref, cell):
    """A cell is text (wrapped), or a dict: {"t": text}, {"money": cents} or {"n": number}, each with an optional
    "s" style and "f" formula (the value is then the cached result). {"s": style} alone is an empty styled cell."""
    if isinstance(cell, str):
        cell = {"t": cell, "s": WRAP}
    f = "<f>{}</f>".format(xml(cell["f"])) if "f" in cell else ""
    if "money" in cell:
        return '<c r="{}" s="{}">{}<v>{}</v></c>'.format(ref, cell.get("s", MONEY), f, dollars(cell["money"]))
    if "n" in cell:
        return '<c r="{}" s="{}">{}<v>{}</v></c>'.format(ref, cell.get("s", PLAIN), f, cell["n"])
    if f:
        return '<c r="{}" t="str" s="{}">{}<v>{}</v></c>'.format(ref, cell.get("s", PLAIN), f, xml(cell["t"]))
    if cell.get("t"):
        return '<c r="{}" t="inlineStr" s="{}"><is><t xml:space="preserve">{}</t></is></c>'.format(ref, cell.get("s", PLAIN), xml(cell["t"]))
    return '<c r="{}" s="{}"/>'.format(ref, cell.get("s", PLAIN))


def sheet_xml(rows, widths, freeze_cols, freeze_rows, tail=""):
    """One worksheet, printed landscape and one page wide. `tail` is the XML that follows the cells: filter,
    conditional formats, validation."""
    out = []
    for r, row in enumerate(rows):
        cells = "".join(cell_xml("{}{}".format(col(c), r + 1), cell) for c, cell in enumerate(row) if cell is not None and cell != "")
        out.append('<row r="{}">{}</row>'.format(r + 1, cells))
    cols = "".join('<col min="{0}" max="{0}" width="{1}" customWidth="1"/>'.format(i + 1, w) for i, w in enumerate(widths))
    pane = '<pane {}ySplit="{}" topLeftCell="{}{}" activePane="{}" state="frozen"/>'.format(
        'xSplit="{}" '.format(freeze_cols) if freeze_cols else "", freeze_rows, col(freeze_cols), freeze_rows + 1,
        "bottomRight" if freeze_cols else "bottomLeft")
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetPr><pageSetUpPr fitToPage="1"/></sheetPr>'
            '<sheetViews><sheetView workbookViewId="0">{}</sheetView></sheetViews><cols>{}</cols><sheetData>{}</sheetData>{}'
            '<pageSetup orientation="landscape" fitToHeight="0"/></worksheet>'.format(pane, cols, "".join(out), tail))


def bid_tab(data, results):
    """The Bid tab: one row per scope item, two columns per bidder (what the bid says, and the plug)."""
    last_col = col(2 * len(results))
    addenda = _addenda(data["addenda"]) if data["addenda"] else "No addenda"
    rows = [[{"t": "{}: {}".format(data["project"], data["package"]), "s": TITLE}]]
    rows += [[{"t": note.format(asOf=data["asOf"], addenda=addenda)}] for note in NOTES]
    rows.append([{"t": "Scope item", "s": HEAD}] + [h for r in results for h in ({"t": r["bid"]["bidder"], "s": HEAD}, {"t": "Plug", "s": HEAD})])
    header_rows = len(rows)
    formats, gaps, priority = [], [[] for _ in results], 0

    def scope_row(index):
        nonlocal priority
        row = data["scope"][index]
        line = [row["label"]]
        for b, r in enumerate(results):
            item = r["cells"][index]
            ref = "{}{}".format(col(2 + 2 * b), len(rows) + 1)
            flagged = item["gap"] or (row.get("extra") and item["cell"]["status"] != "omitted")
            line.append({"t": says(item["cell"]), "s": FLAG if flagged else WRAP})
            line.append(dict({"s": INPUT if flagged else MONEY}, **({} if item["amount"] is None else {"money": item["amount"]})))
            if item["gap"]:
                gaps[b].append(ref)
                rules = '<cfRule type="expression" dxfId="{}" priority="{}"><formula>ISBLANK({})</formula></cfRule>'.format(DXF_OPEN, priority + 1, ref)
                if item["suggested"]:
                    rules += '<cfRule type="cellIs" dxfId="{}" priority="{}" operator="equal"><formula>{}</formula></cfRule>'.format(
                        DXF_SUGGESTED, priority + 2, dollars(item["amount"]))
                priority += 2
                formats.append('<conditionalFormatting sqref="{}">{}</conditionalFormatting>'.format(ref, rules))
        rows.append(line)

    first = len(rows) + 1
    for index, row in enumerate(data["scope"]):
        if not row.get("extra"):
            scope_row(index)
    if any(row.get("extra") for row in data["scope"]):
        rows.append([{"t": "Not on the scope sheet (raised in a bid)", "s": BOLD}])
        for index, row in enumerate(data["scope"]):
            if row.get("extra"):
                scope_row(index)
    last = len(rows)
    rows.append([])
    base_n, plugs_n, leveled_n, open_n, rank_n = (len(rows) + i for i in (1, 2, 3, 4, 6))

    def across(n):
        return "$B${0}:${1}${0}".format(n, last_col)

    def total(label, make):
        # Each bidder's figure sits in its Plug column, under the plugs it adds up.
        rows.append([{"t": label, "s": BOLD}] + [x for b, r in enumerate(results) for x in (None, make(b, r, col(2 + 2 * b)))])

    total("Base bid", lambda b, r, c: {"money": r["base"]})
    total("Plugs", lambda b, r, c: {"money": r["plugs"], "f": "SUM({0}{1}:{0}{2})".format(c, first, last)})
    total("Leveled total", lambda b, r, c: {"money": r["leveled"], "f": "{0}{1}+{0}{2}".format(c, base_n, plugs_n), "s": MONEY_BOLD})
    total("Gaps without a plug", lambda b, r, c: dict({"n": r["open"]}, **({"f": "+".join("COUNTBLANK({})".format(g) for g in gaps[b])} if gaps[b] else {})))
    total("Rank by base bid", lambda b, r, c: {"n": r["base_rank"], "f": 'COUNTIF({},"<"&{}{})+1'.format(across(base_n), c, base_n)})
    total("Rank by leveled total", lambda b, r, c: dict(
        {"n": r["rank"]} if r["complete"] else {"t": "Incomplete"}, s=RIGHT,
        f='IF({0}{1}>0,"Incomplete",COUNTIFS({2},"<"&{0}{3},{4},0)+1)'.format(c, open_n, across(leveled_n), leveled_n, across(open_n))))

    def addenda_text(r):
        acked = r["bid"].get("addenda")
        if acked is None:
            return "Not stated"
        text = ", ".join(str(n) for n in acked) if acked else "None"
        return text + (" (missing {})".format(", ".join(str(n) for n in r["missing"])) if r["missing"] else "")

    for label, text in (("Addenda acknowledged", addenda_text), ("Notes", lambda r: " ".join(r["bid"].get("notes") or [])),
                        ("Bid file", lambda r: r["bid"]["file"])):
        rows.append([{"t": label, "s": BOLD}] + [x for r in results for x in (text(r), None)])

    plug_cols = " ".join("{0}{1}:{0}{2}".format(col(2 + 2 * b), first, last) for b in range(len(results)))
    tail = "".join(formats) + (
        '<conditionalFormatting sqref="B{0}:{1}{0}"><cfRule type="cellIs" dxfId="{2}" priority="{3}" operator="equal"><formula>1</formula></cfRule>'
        "</conditionalFormatting>".format(rank_n, last_col, DXF_LOW, priority + 1)
        + '<dataValidations count="1"><dataValidation type="decimal" allowBlank="1" showErrorMessage="1" errorTitle="Plug" '
        'error="Enter a dollar amount. Use 0 when the bidder confirms the item is in their price." sqref="{}">'
        "<formula1>-999999999</formula1><formula2>999999999</formula2></dataValidation></dataValidations>".format(plug_cols))
    return sheet_xml(rows, [40] + [36, 15] * len(results), 1, header_rows, tail)


def review_tab(results):
    """The Review sheet: one row per flag, with the reason and the question to ask the bidder."""
    rows = [[{"t": t, "s": HEAD} for t in ("Flag", "Bidder", "Scope item", "Bid says", "Why it's flagged", "Ask the bidder")]]
    rows += [[f["flag"], f["bidder"], f["scope"], f["says"], f["why"], f["ask"]] for r in results for f in r["review"]]
    return sheet_xml(rows, [19, 30, 36, 44, 60, 70], 0, 1, '<autoFilter ref="A1:F{}"/>'.format(len(rows)))


def workbook(data, analysis=None):
    results = (analysis or level(data))["results"]
    sheets = [("Bid tab", bid_tab(data, results)), ("Review", review_tab(results))]
    head = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    ns = "http://schemas.openxmlformats.org"
    files = [
        ("[Content_Types].xml", head + '<Types xmlns="{0}/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
         '<Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
         '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>{1}</Types>'.format(
             ns, "".join('<Override PartName="/xl/worksheets/sheet{}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'.format(i + 1) for i in range(len(sheets))))),
        ("_rels/.rels", head + '<Relationships xmlns="{0}/package/2006/relationships"><Relationship Id="rId1" Type="{0}/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'.format(ns)),
        ("xl/workbook.xml", head + '<workbook xmlns="{0}/spreadsheetml/2006/main" xmlns:r="{0}/officeDocument/2006/relationships"><sheets>{1}</sheets><calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>'.format(
            ns, "".join('<sheet name="{}" sheetId="{}" r:id="rId{}"/>'.format(xml(name), i + 1, i + 1) for i, (name, _) in enumerate(sheets)))),
        ("xl/_rels/workbook.xml.rels", head + '<Relationships xmlns="{0}/package/2006/relationships">{1}<Relationship Id="rId{2}" Type="{0}/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'.format(
            ns, "".join('<Relationship Id="rId{0}" Type="{1}/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{0}.xml"/>'.format(i + 1, ns) for i in range(len(sheets))), len(sheets) + 1)),
        ("xl/styles.xml", head + '<styleSheet xmlns="{}/spreadsheetml/2006/main">{}</styleSheet>'.format(ns, STYLES)),
    ] + [("xl/worksheets/sheet{}.xml".format(i + 1), body) for i, (_, body) in enumerate(sheets)]

    # Stored entries with a fixed timestamp and attributes, so the output is reproducible.
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_STORED) as archive:
        for name, text in files:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 0
            info.external_attr = 0
            archive.writestr(info, text.encode("utf-8"))
    return buffer.getvalue()


def summary(analysis):
    """What the workbook opens with, as text for whoever ran the script."""
    low, base = analysis["lowest_complete"], analysis["lowest_base"]
    lines = ["Lowest base bid: {} at {}".format(base["bid"]["bidder"], money(base["base"])),
             "Lowest complete leveled total: {}".format(
                 "{} at {}".format(low["bid"]["bidder"], money(low["leveled"])) if low else "none (every bid has a gap without a plug)")]
    for r in analysis["results"]:
        lines.append("- {}: {} base + {} plugs = {} leveled, {}".format(
            r["bid"]["bidder"], money(r["base"]), money(r["plugs"]), money(r["leveled"]),
            "complete" if r["complete"] else "incomplete ({} gap{} without a plug)".format(r["open"], "" if r["open"] == 1 else "s")))
    flags = Counter(f["flag"] for r in analysis["results"] for f in r["review"])
    lines.append("Flagged for review: " + (", ".join("{} {}".format(n, kind) for kind, n in flags.items()) if flags else "nothing"))
    return "\n".join(lines)


def main(argv):
    if len(argv) != 2 or argv[0].startswith("-"):
        print("Usage: python3 level.py bid-data.json bid-tab.xlsx", file=sys.stderr)
        return 2
    data_path, out_path = argv
    try:
        with open(data_path, encoding="utf-8") as f:
            data = validate(json.load(f))
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    analysis = level(data)
    with open(out_path, "wb") as f:
        f.write(workbook(data, analysis))
    print("Wrote {} (sheets: Bid tab, Review).\n{}".format(out_path, summary(analysis)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
