#!/usr/bin/env python3
"""Level sub bids into one Excel workbook with live formulas.

    python3 level.py bid-data.json bid-tab.xlsx
    python3 level.py bid-data.json --json      (print the leveled totals instead)

Standard library only, Python 3.8 or newer. Money in the JSON is dollars; the
script works in integer cents.
"""

import json
import math
import re
import sys
import zipfile
from io import BytesIO

STATUSES = ["included", "excluded", "omitted", "unclear"]
KEY = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


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
    need(len(scope) > 0, "scope must list at least one scope line")
    keys = []
    for row in scope:
        row = row if isinstance(row, dict) else {}
        key = row.get("key")
        need(isinstance(key, str) and KEY.match(key) and key not in keys,
             'scope key "{}" must be unique: lowercase letters, digits, - or _'.format(key))
        need(is_text(row.get("label")), 'scope line "{}" needs a label'.format(key))
        keys.append(key)
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
        for field in ("notes", "questions"):
            value = bid.get(field)
            need(value is None or (isinstance(value, list) and all(is_text(t) for t in value)), "{}: {} must be a list of text".format(who, field))
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
        if bid is not None and plug.get("scope") in keys:
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


def _addenda(numbers):
    return "Addend{} {}".format("um" if len(numbers) == 1 else "a", " and ".join(str(n) for n in numbers))


def level(data):
    entered = {(p["bidder"], p["scope"]): p for p in data.get("plugs") or []}
    results = []
    for bid in data["bids"]:
        gaps = []
        questions = []
        acked = bid.get("addenda")
        missing = [n for n in data["addenda"] if n not in acked] if acked is not None else []
        if acked is None and data["addenda"]:
            questions.append("Your bid doesn't say which addenda it covers. Confirm it includes Addenda {}.".format(" and ".join(str(n) for n in data["addenda"])))
        if missing:
            questions.append("Your bid acknowledges {}. Confirm you received {} and that your price covers {}.".format(
                _addenda(acked) if acked else "no addenda", _addenda(missing), "it" if len(missing) == 1 else "them"))
        for row in data["scope"]:
            cell = bid["scope"][row["key"]]
            if cell["status"] == "included":
                continue
            plug = entered.get((bid["bidder"], row["key"]))
            suggestion = None if cell["status"] == "unclear" else suggest(data, bid, row["key"])
            if plug:
                gap = {"amount": cents(plug["amount"]), "source": "Entered: " + plug["source"]}
            elif suggestion:
                gap = {"amount": suggestion["amount"], "source": "Suggested: {} itemized {} for this line".format(suggestion["bidder"], money(suggestion["amount"]))}
            elif cell["status"] == "unclear":
                gap = {"amount": None, "source": "Open: ask the bidder what the wording covers"}
            else:
                gap = {"amount": None, "source": "Open: no other bid itemizes this line"}
            gap.update(row=row, cell=cell, carry=gap["amount"] is not None)
            gaps.append(gap)
            questions.append(QUESTION[cell["status"]](row["label"], cell.get("quote")))
        questions.extend(bid.get("questions") or [])
        base = cents(bid["total"])
        plugs = sum(g["amount"] for g in gaps if g["carry"])
        open_gaps = sum(1 for g in gaps if not g["carry"])
        results.append({"bid": bid, "base": base, "plugs": plugs, "leveled": base + plugs, "open": open_gaps,
                        "complete": open_gaps == 0, "gaps": gaps, "questions": questions, "missing": missing})
    complete = [r for r in results if r["complete"]]
    lowest_complete = min(complete, key=lambda r: r["leveled"]) if complete else None
    lowest_base = min(results, key=lambda r: r["base"])
    return {"results": results, "lowest_base": lowest_base, "lowest_complete": lowest_complete}


# ---------- XLSX ----------

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


def sheet_xml(rows, widths):
    """Cells: text, {"bold": text}, {"money": cents}, or a formula with its cached value:
    {"f", "money"} or {"f", "n"} or {"f", "text"}. Formulas take "bold". None is empty."""
    out = []
    for r, row in enumerate(rows):
        cells = []
        for c, cell in enumerate(row):
            if cell is None or cell == "":
                continue
            ref = "{}{}".format(col(c), r + 1)
            if isinstance(cell, str):
                cells.append('<c r="{}" t="inlineStr" s="{}"><is><t xml:space="preserve">{}</t></is></c>'.format(ref, 1 if r == 0 else 4, xml(cell)))
                continue
            f = "<f>{}</f>".format(xml(cell["f"])) if "f" in cell else ""
            if "money" in cell:
                cells.append('<c r="{}" s="{}">{}<v>{}</v></c>'.format(ref, 3 if cell.get("bold") else 2, f, dollars(cell["money"])))
            elif "n" in cell:
                cells.append('<c r="{}">{}<v>{}</v></c>'.format(ref, f, cell["n"]))
            elif "text" in cell:
                cells.append('<c r="{}" t="str"{}>{}<v>{}</v></c>'.format(ref, ' s="1"' if cell.get("bold") else "", f, xml(cell["text"])))
            else:
                cells.append('<c r="{}" t="inlineStr" s="1"><is><t xml:space="preserve">{}</t></is></c>'.format(ref, xml(cell["bold"])))
        out.append('<row r="{}">{}</row>'.format(r + 1, "".join(cells)))
    cols = "".join('<col min="{0}" max="{0}" width="{1}" customWidth="1"/>'.format(i + 1, w) for i, w in enumerate(widths))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0">'
            '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
            "<cols>{}</cols><sheetData>{}</sheetData></worksheet>".format(cols, "".join(out)))


SAYS = {"excluded": "Excluded", "omitted": "Not mentioned", "unclear": "Unclear"}


def _says(cell):
    return '{}: "{}"'.format(SAYS[cell["status"]], cell["quote"]) if cell.get("quote") else SAYS[cell["status"]]


def workbook(data, analysis=None):
    analysis = analysis or level(data)
    results = analysis["results"]

    plugs = [["Bidder", "Scope", "Bid says", "Plug", "Source", "Carry (Yes/No)"]]
    for r in results:
        for g in r["gaps"]:
            plugs.append([r["bid"]["bidder"], g["row"]["label"], _says(g["cell"]),
                          None if g["amount"] is None else {"money": g["amount"]}, g["source"], "Yes" if g["carry"] else "No"])

    last = len(results) + 1

    def rng(c):
        return "${0}$2:${0}${1}".format(c, last)

    totals = [["Bidder", "Base bid", "Plugs", "Leveled total", "Open gaps", "Status", "Bid file", "Notes"]]
    for i, r in enumerate(results):
        n = i + 2
        totals.append([
            r["bid"]["bidder"],
            {"money": r["base"]},
            {"f": 'SUMIFS(Plugs!$D:$D,Plugs!$A:$A,$A{0},Plugs!$F:$F,"Yes")'.format(n), "money": r["plugs"]},
            {"f": "B{0}+C{0}".format(n), "money": r["leveled"], "bold": True},
            {"f": 'COUNTIFS(Plugs!$A:$A,$A{0})-COUNTIFS(Plugs!$A:$A,$A{0},Plugs!$F:$F,"Yes",Plugs!$D:$D,"<>")'.format(n), "n": r["open"]},
            {"f": 'IF(E{0}=0,"Complete","Incomplete")'.format(n), "text": "Complete" if r["complete"] else "Incomplete"},
            r["bid"]["file"],
            " ".join(r["bid"].get("notes") or []),
        ])
    any_complete = "COUNTIF({},0)=0".format(rng("E"))
    lowest_row = "MATCH(1,INDEX(({0}=_xlfn.MINIFS({0},{1},0))*({1}=0),0),0)".format(rng("D"), rng("E"))
    low_base, low_complete = analysis["lowest_base"], analysis["lowest_complete"]
    totals += [
        [],
        [{"bold": "Lowest"}, {"bold": "Bidder"}, None, {"bold": "Amount"}],
        [
            "Base bid",
            {"f": "INDEX({0},MATCH(MIN({1}),{1},0))".format(rng("A"), rng("B")), "text": low_base["bid"]["bidder"]},
            None,
            {"f": "MIN({})".format(rng("B")), "money": low_base["base"]},
        ],
        [
            "Complete leveled total",
            {"f": 'IF({},"None complete",INDEX({},{}))'.format(any_complete, rng("A"), lowest_row),
             "text": low_complete["bid"]["bidder"] if low_complete else "None complete", "bold": True},
            None,
            dict({"f": 'IF({},"",_xlfn.MINIFS({},{},0))'.format(any_complete, rng("D"), rng("E")), "bold": True},
                 **({"money": low_complete["leveled"]} if low_complete else {"text": ""})),
        ],
        [],
        ['Leveled total = base bid + plugs marked Carry "Yes" on the Plugs sheet. A bid is complete when every gap carries a plug. '
         'Suggested plugs are the highest price another bidder itemized for the same line; change the amount, or set Carry to "No", '
         "on the Plugs sheet. As of {}. This is a comparison, not an award recommendation.".format(data["asOf"])],
    ]

    scope = [["Scope"] + [r["bid"]["bidder"] for r in results]]
    for row in data["scope"]:
        line = [row["label"]]
        for r in results:
            cell = r["bid"]["scope"][row["key"]]
            if cell["status"] == "included":
                line.append("Included" if "amount" not in cell else "Included " + money(cents(cell["amount"])))
            else:
                line.append(_says(cell))
        scope.append(line)

    def addenda_text(r):
        acked = r["bid"].get("addenda")
        if acked is None:
            return "Not stated"
        text = ", ".join(str(n) for n in acked) if acked else "None"
        return text + (" (missing {})".format(", ".join(str(n) for n in r["missing"])) if r["missing"] else "")

    scope.append([{"bold": "Addenda"}] + [addenda_text(r) for r in results])
    scope.append([{"bold": "Base bid"}] + [{"money": r["base"]} for r in results])

    questions = [["Bidder", "Question"]]
    for r in results:
        questions += [[r["bid"]["bidder"], q] for q in r["questions"]]

    sheets = [
        ("Leveled totals", sheet_xml(totals, [32, 16, 14, 16, 11, 13, 26, 60])),
        ("Scope", sheet_xml(scope, [40] + [34] * len(results))),
        ("Plugs", sheet_xml(plugs, [30, 36, 50, 14, 56, 14])),
        ("Questions", sheet_xml(questions, [30, 100])),
    ]
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
        ("xl/styles.xml", head + '<styleSheet xmlns="{}/spreadsheetml/2006/main"><numFmts count="1"><numFmt numFmtId="164" formatCode="&quot;$&quot;#,##0.00"/></numFmts>'
         '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
         '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders count="1"><border/></borders>'
         '<cellStyleXfs count="1"><xf/></cellStyleXfs><cellXfs count="5"><xf/><xf fontId="1" applyFont="1"/><xf numFmtId="164" applyNumberFormat="1"/>'
         '<xf numFmtId="164" fontId="1" applyNumberFormat="1" applyFont="1"/><xf applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf></cellXfs></styleSheet>'.format(ns)),
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


def _number(c):
    return c // 100 if c % 100 == 0 else c / 100


def main(argv):
    if len(argv) != 2:
        print("Usage: python3 level.py bid-data.json bid-tab.xlsx\n       python3 level.py bid-data.json --json", file=sys.stderr)
        return 2
    data_path, out_path = argv
    try:
        with open(data_path, encoding="utf-8") as f:
            data = validate(json.load(f))
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    analysis = level(data)
    if out_path == "--json":
        summary = [{
            "bidder": r["bid"]["bidder"],
            "base": _number(r["base"]),
            "plugs": _number(r["plugs"]),
            "leveled": _number(r["leveled"]),
            "openGaps": r["open"],
            "gaps": [{"scope": g["row"]["key"], "status": g["cell"]["status"],
                      "plug": None if g["amount"] is None else _number(g["amount"]), "source": g["source"]} for g in r["gaps"]],
            "questions": r["questions"],
        } for r in analysis["results"]]
        low = analysis["lowest_complete"]
        print(json.dumps({"lowestBase": analysis["lowest_base"]["bid"]["bidder"],
                          "lowestComplete": low["bid"]["bidder"] if low else None, "results": summary}, indent=2, ensure_ascii=False))
        return 0
    with open(out_path, "wb") as f:
        f.write(workbook(data, analysis))
    low = analysis["lowest_complete"]
    print("Wrote {}. Lowest complete: {}.".format(
        out_path, "{} at {}".format(low["bid"]["bidder"], money(low["leveled"])) if low else "none (every bid has an open gap)"), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
