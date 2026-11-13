import copy
import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO
from pathlib import Path

SKILL = Path(__file__).resolve().parents[3] / "skills" / "bid-leveling"
SCRIPT = SKILL / "scripts" / "level.py"
sys.path.insert(0, str(SCRIPT.parent))
sys.dont_write_bytecode = True

from level import BidDataError, level, money, validate, workbook  # noqa: E402

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
FLAG_STYLE, INPUT_STYLE = 7, 8


def sample():
    return json.loads((SKILL / "samples" / "bid-data.json").read_text(encoding="utf-8"))


def pkg(**overrides):
    """A small package for rule-level tests: A excludes batts, B and C itemize everything.

    On the Bid tab, A is columns B/C, B is D/E and C is F/G. Framing is row 6, batts row 7, and the
    totals start at row 9: base, plugs, leveled, gaps without a plug, rank by base, rank by leveled.
    """
    def inc(amount=None):
        return {"status": "included", "quote": "Included."} if amount is None else {"status": "included", "amount": amount, "quote": "$%s" % amount}

    def bid(bidder, total, scope):
        return {"bidder": bidder, "file": bidder + ".md", "total": total, "addenda": [1], "scope": scope}

    data = {
        "project": "Test Clinic",
        "package": "Drywall",
        "asOf": "2027-03-02",
        "addenda": [1],
        "scope": [{"key": "framing", "label": "Framing"}, {"key": "batts", "label": "Sound batts"}],
        "bids": [
            bid("A", 1000, {"framing": inc(), "batts": {"status": "excluded", "quote": "Batts by others."}}),
            bid("B", 1200, {"framing": inc(900), "batts": inc(150)}),
            bid("C", 1100, {"framing": inc(950), "batts": inc(200)}),
        ],
        "plugs": [],
    }
    data.update(overrides)
    return data


def with_extra(data):
    """Add a line the scope sheet doesn't list: A excludes it, B carries $300 of it, C never mentions it."""
    data["scope"].append({"key": "act", "label": "ACT ceilings", "extra": True})
    data["bids"][0]["scope"]["act"] = {"status": "excluded", "quote": "ACT ceilings NIC."}
    data["bids"][1]["scope"]["act"] = {"status": "included", "amount": 300, "quote": "ACT ceilings $300"}
    data["bids"][2]["scope"]["act"] = {"status": "omitted"}
    return data


def result(data, bidder):
    return next(r for r in level(validate(data))["results"] if r["bid"]["bidder"] == bidder)


def flags(data, bidder):
    return [(f["flag"], f["scope"]) for f in result(data, bidder)["review"]]


def parts(data):
    archive = zipfile.ZipFile(BytesIO(workbook(validate(data))))
    return {name: archive.read(name).decode("utf-8") for name in archive.namelist()}


def cells(sheet):
    """Every cell of a worksheet by reference: style index, formula, and value (cached for formulas)."""
    out = {}
    for c in ET.fromstring(sheet).iterfind(".//m:c", NS):
        f, v, t = c.find("m:f", NS), c.find("m:v", NS), c.find("m:is/m:t", NS)
        out[c.get("r")] = {"s": int(c.get("s", 0)), "f": None if f is None else f.text,
                           "v": v.text if v is not None else (None if t is None else t.text)}
    return out


def run(*args):
    return subprocess.run([sys.executable, "-I", str(SCRIPT), *args], capture_output=True, text=True)


class LevelTest(unittest.TestCase):
    def test_bundled_workbook_matches_a_fresh_build_exactly(self):
        self.assertEqual(workbook(validate(sample())), (SKILL / "samples" / "output-bid-tab.xlsx").read_bytes())

    def test_sample_lowest_base_is_not_lowest_complete(self):
        analysis = level(validate(sample()))
        by = {r["bid"]["bidder"].split()[0]: r for r in analysis["results"]}
        self.assertEqual(analysis["lowest_base"]["bid"]["bidder"], "Northgate Drywall & Acoustics")
        self.assertEqual(analysis["lowest_complete"]["bid"]["bidder"], "Prairie Wall & Ceiling Co.")
        self.assertEqual((by["Northgate"]["leveled"], by["Northgate"]["open"], by["Northgate"]["rank"]), (80780000, 1, None))
        self.assertEqual((by["Prairie"]["leveled"], by["Prairie"]["open"], by["Prairie"]["rank"]), (80380000, 0, 1))
        self.assertEqual((by["Ridgeline"]["leveled"], by["Ridgeline"]["open"], by["Ridgeline"]["rank"]), (82210000, 0, 2))
        self.assertEqual([by[name]["base_rank"] for name in ("Northgate", "Prairie", "Ridgeline")], [1, 3, 2])
        self.assertEqual([f["flag"] for f in by["Northgate"]["review"]],
                         ["Addenda", "Suggested plug", "Suggested plug", "Needs a plug", "Not on scope sheet"])
        self.assertIn("Confirm you received Addendum 2", by["Northgate"]["review"][0]["ask"])
        self.assertEqual(by["Prairie"]["review"], [])
        self.assertEqual(by["Ridgeline"]["review"][-1]["flag"], "Check")
        self.assertIn("$781,000", by["Ridgeline"]["review"][-1]["ask"])

    def test_suggested_plugs_use_the_highest_itemized_price_and_count_by_default(self):
        a = result(pkg(), "A")
        batts = a["cells"][1]
        self.assertEqual((batts["gap"], batts["amount"], batts["suggested"]), (True, 20000, True))
        self.assertEqual((a["plugs"], a["leveled"], a["complete"]), (20000, 120000, True))
        self.assertEqual(flags(pkg(), "A"), [("Suggested plug", "Sound batts")])
        self.assertIn("Plug of $200 is the highest price another bidder itemized for this line (C).", a["review"][0]["why"])
        self.assertIn('Your bid says "Batts by others." Confirm your bid excludes sound batts', a["review"][0]["ask"])

    def test_unclear_scope_or_scope_nobody_itemizes_stays_open(self):
        unclear = pkg()
        unclear["bids"][0]["scope"]["batts"] = {"status": "unclear", "quote": "Insulation per plans."}
        a = result(unclear, "A")
        self.assertEqual((a["cells"][1]["amount"], a["open"], a["complete"], a["leveled"], a["rank"]), (None, 1, False, 100000, None))
        self.assertEqual(a["review"][0]["flag"], "Needs a plug")
        self.assertIn("Does your base bid include sound batts?", a["review"][0]["ask"])

        nobody = pkg()
        for bid in nobody["bids"][1:]:
            bid["scope"]["batts"] = {"status": "included", "quote": "Batts."}
        a = result(nobody, "A")
        self.assertEqual((a["open"], a["review"][0]["flag"]), (1, "Needs a plug"))
        self.assertIn("No other bid itemizes this line", a["review"][0]["why"])

    def test_entered_plugs_replace_suggestions_and_need_a_gap_and_a_source(self):
        a = result(pkg(plugs=[{"bidder": "A", "scope": "batts", "amount": 175.5, "source": "GC budget line 0921"}]), "A")
        self.assertEqual((a["cells"][1]["amount"], a["cells"][1]["suggested"], a["leveled"]), (17550, False, 117550))
        self.assertEqual((a["review"][0]["flag"], a["review"][0]["why"]), ("Your plug", "Plug of $175.50 entered. Source: GC budget line 0921."))

        # A $0 plug closes the gap: the bidder confirmed the line is in their price.
        confirmed = result(pkg(plugs=[{"bidder": "A", "scope": "batts", "amount": 0, "source": "Bidder confirmed by phone"}]), "A")
        self.assertEqual((confirmed["open"], confirmed["leveled"], confirmed["rank"]), (0, 100000, 1))

        bad = pkg(plugs=[
            {"bidder": "B", "scope": "batts", "amount": 10, "source": "x"},
            {"bidder": "A", "scope": "batts", "amount": 10, "source": ""},
            {"bidder": "Z", "scope": "batts", "amount": 10, "source": "x"},
        ])
        with self.assertRaises(BidDataError) as raised:
            validate(bad)
        for text in ("nothing to plug", "say where the figure came from", 'no bid from "Z"'):
            self.assertIn(text, str(raised.exception))

    def test_lines_not_on_the_scope_sheet_are_flagged_but_never_gaps(self):
        data = with_extra(pkg())
        a, b, c = (result(data, name) for name in "ABC")
        # Nobody is incomplete over the extra line, and B's $300 is never suggested as a plug for A or C.
        self.assertEqual([(r["open"], r["plugs"]) for r in (a, b, c)], [(0, 20000), (0, 0), (0, 0)])
        self.assertEqual(flags(data, "A"), [("Suggested plug", "Sound batts"), ("Not on scope sheet", "ACT ceilings")])
        self.assertEqual(flags(data, "B"), [("Not on scope sheet", "ACT ceilings")])
        self.assertEqual(flags(data, "C"), [])
        self.assertEqual(b["review"][0]["says"], 'Included: "ACT ceilings $300"')
        self.assertIn("What would you deduct to take it out?", b["review"][0]["ask"])
        self.assertEqual(a["review"][1]["ask"], "")

        # An entered deduct takes B's extra scope out of its leveled total.
        data["plugs"] = [{"bidder": "B", "scope": "act", "amount": -300, "source": "B's own line item"}]
        b = result(data, "B")
        self.assertEqual((b["plugs"], b["leveled"], b["rank"]), (-30000, 90000, 1))
        self.assertIn("Plug of -$300 entered. Source: B's own line item.", b["review"][0]["why"])

        only_extra = pkg(scope=[{"key": "framing", "label": "Framing", "extra": True}, {"key": "batts", "label": "Sound batts", "extra": True}])
        with self.assertRaisesRegex(BidDataError, "at least one scope line that isn't extra"):
            validate(only_extra)

    def test_validation_refuses_incomplete_or_uncited_extractions(self):
        data = pkg()
        del data["bids"][0]["scope"]["framing"]
        data["bids"][1]["scope"]["batts"] = {"status": "excluded"}
        data["bids"][2]["scope"]["framing"] = {"status": "omitted", "amount": 5}
        data["bids"][2]["total"] = 10.005
        data["bids"][2]["review"] = [{"ask": "A question with nothing to check"}]
        data["bids"][0]["review"] = [{"check": "About a line that isn't on the sheet.", "scope": "roofing"}]
        data["bids"].append(copy.deepcopy(data["bids"][1]))
        with self.assertRaises(BidDataError) as raised:
            validate(data)
        for text in ('no entry for scope line "framing"', "B / batts: quote the bid's words", "only included lines carry an amount",
                     "C: total must be", "A: review must be a list", "C: review must be a list", 'bidder "B" must be named and unique'):
            self.assertIn(text, str(raised.exception))
        with self.assertRaisesRegex(BidDataError, "at least two bids"):
            validate(pkg(bids=pkg()["bids"][:1]))
        true_total = pkg()
        true_total["bids"][0]["total"] = True
        with self.assertRaisesRegex(BidDataError, "A: total must be"):
            validate(true_total)

    def test_missing_or_unstated_addenda_are_flagged_with_a_question(self):
        data = pkg(addenda=[1, 2])
        data["bids"][2]["addenda"] = None
        a, c = result(data, "A")["review"][0], result(data, "C")["review"][0]
        self.assertEqual((a["flag"], a["why"]), ("Addenda", "The bid acknowledges Addendum 1, not Addendum 2."))
        self.assertRegex(a["ask"], r"acknowledges Addendum 1\. Confirm you received Addendum 2")
        self.assertEqual(c["flag"], "Addenda")
        self.assertIn("doesn't say which addenda", c["ask"])

    def test_bid_tab_lists_every_scope_item_with_a_plug_cell_per_bidder(self):
        files = parts(with_extra(pkg()))
        self.assertIn('fullCalcOnLoad="1"', files["xl/workbook.xml"])
        self.assertRegex(files["xl/workbook.xml"], r'name="Bid tab".*name="Review"')
        self.assertNotIn("sheet3", files["[Content_Types].xml"])
        tab = cells(files["xl/worksheets/sheet1.xml"])
        self.assertEqual([tab[ref]["v"] for ref in ("A5", "B5", "C5", "D5", "E5", "F5", "G5")], ["Scope item", "A", "Plug", "B", "Plug", "C", "Plug"])
        self.assertEqual([tab[ref]["v"] for ref in ("A6", "A7", "A8", "A9")], ["Framing", "Sound batts", "Not on the scope sheet (raised in a bid)", "ACT ceilings"])
        self.assertEqual([tab[ref]["v"] for ref in ("B6", "D6", "F6")], ["Included", "Included $900", "Included $950"])
        self.assertEqual([tab[ref]["v"] for ref in ("B7", "D7", "F7")], ['Excluded: "Batts by others."', "Included $150", "Included $200"])
        self.assertEqual([tab[ref]["v"] for ref in ("B9", "D9", "F9")], ['Excluded: "ACT ceilings NIC."', "Included $300", "Not mentioned"])
        # Flagged cells are filled and get a yellow plug cell; the rest are plain. A's gap carries the suggestion.
        self.assertEqual([tab[ref]["s"] for ref in ("B7", "C7", "B9", "C9", "D9", "E9")], [FLAG_STYLE, INPUT_STYLE] * 3)
        self.assertEqual([tab[ref]["s"] for ref in ("B6", "D7", "F9")], [4, 4, 4])
        self.assertEqual((tab["C7"]["v"], tab["C9"]["v"], tab["E7"]["v"]), ("200", None, None))
        # Every plug cell under a bidder takes a dollar amount and nothing else.
        self.assertRegex(files["xl/worksheets/sheet1.xml"], r'<dataValidation type="decimal"[^>]*sqref="C6:C9 E6:E9 G6:G9"')

    def test_totals_are_formulas_over_the_plug_cells_with_cached_values(self):
        data = pkg()
        data["bids"][0]["scope"]["framing"] = {"status": "unclear", "quote": "Framing & board."}
        sheet = parts(data)["xl/worksheets/sheet1.xml"]
        tab = cells(sheet)
        self.assertEqual((tab["B6"]["v"], tab["B6"]["s"], tab["C6"]["v"]), ('Unclear: "Framing & board."', FLAG_STYLE, None))
        self.assertEqual((tab["C9"]["f"], tab["C9"]["v"]), (None, "1000"))
        self.assertEqual((tab["C10"]["f"], tab["C10"]["v"]), ("SUM(C6:C7)", "200"))
        self.assertEqual((tab["C11"]["f"], tab["C11"]["v"]), ("C9+C10", "1200"))
        self.assertEqual((tab["C12"]["f"], tab["C12"]["v"]), ("COUNTBLANK(C6)+COUNTBLANK(C7)", "1"))
        self.assertEqual((tab["E12"]["f"], tab["E12"]["v"]), (None, "0"))
        self.assertEqual((tab["C13"]["f"], tab["C13"]["v"]), ('COUNTIF($B$9:$G$9,"<"&C9)+1', "1"))
        self.assertEqual([tab[ref]["v"] for ref in ("C13", "E13", "G13")], ["1", "3", "2"])
        # A is incomplete, so the lowest complete is C at $1,100, then B at $1,200.
        self.assertEqual(tab["G14"]["f"], 'IF(G12>0,"Incomplete",COUNTIFS($B$11:$G$11,"<"&G11,$B$12:$G$12,0)+1)')
        self.assertEqual([tab[ref]["v"] for ref in ("C14", "E14", "G14")], ["Incomplete", "2", "1"])
        self.assertEqual([tab[ref]["v"] for ref in ("A15", "B15", "A17", "F17")], ["Addenda acknowledged", "1", "Bid file", "C.md"])
        # A blank gap turns red; a suggestion stays orange until it is typed over; rank 1 turns green.
        self.assertIn('<conditionalFormatting sqref="C6"><cfRule type="expression" dxfId="0" priority="1"><formula>ISBLANK(C6)</formula></cfRule></conditionalFormatting>', sheet)
        self.assertRegex(sheet, r'<conditionalFormatting sqref="C7"><cfRule type="expression" dxfId="0"[^>]*><formula>ISBLANK\(C7\)</formula></cfRule>'
                                r'<cfRule type="cellIs" dxfId="1"[^>]*operator="equal"><formula>200</formula></cfRule>')
        self.assertRegex(sheet, r'<conditionalFormatting sqref="B14:G14"><cfRule type="cellIs" dxfId="2"[^>]*><formula>1</formula>')
        self.assertEqual(sheet.count("<conditionalFormatting"), 3)

    def test_review_sheet_lists_every_flag_with_its_reason_and_question(self):
        data = pkg(addenda=[1, 2])
        data["bids"][2]["review"] = [{"check": "Bid form adds to $1,150; the stated total is $1,100.", "ask": "Which number governs?"},
                                     {"check": "Price is good for 10 days only."},
                                     {"check": "Framing is priced to the original drawings.", "scope": "framing"}]
        sheet = parts(data)["xl/worksheets/sheet2.xml"]
        review = cells(sheet)
        self.assertEqual([review[ref]["v"] for ref in ("A1", "B1", "C1", "D1", "E1", "F1")],
                         ["Flag", "Bidder", "Scope item", "Bid says", "Why it's flagged", "Ask the bidder"])
        self.assertEqual([review[ref]["v"] for ref in ("A2", "B2", "A3", "B3", "C3", "D3")],
                         ["Addenda", "A", "Suggested plug", "A", "Sound batts", 'Excluded: "Batts by others."'])
        self.assertEqual([review[ref]["v"] for ref in ("A6", "B6", "E6", "F6")],
                         ["Check", "C", "Bid form adds to $1,150; the stated total is $1,100.", "Which number governs?"])
        self.assertEqual((review["E7"]["v"], "F7" in review), ("Price is good for 10 days only.", False))
        # A check about one scope line names the line and repeats what the bid says about it.
        self.assertEqual([review[ref]["v"] for ref in ("A8", "C8", "D8")], ["Check", "Framing", "Included $950"])
        self.assertIn('<autoFilter ref="A1:F8"/>', sheet)

    def test_no_complete_bid_is_reported_as_none(self):
        data = pkg()
        for bid in data["bids"]:
            bid["scope"]["batts"] = {"status": "unclear", "quote": "Insulation?"}
        self.assertIsNone(level(validate(data))["lowest_complete"])
        tab = cells(parts(data)["xl/worksheets/sheet1.xml"])
        self.assertEqual([tab[ref]["v"] for ref in ("C14", "E14", "G14")], ["Incomplete"] * 3)

    def test_money_formatting(self):
        self.assertEqual(money(80380000), "$803,800")
        self.assertEqual(money(17550), "$175.50")
        self.assertEqual(money(-950), "-$9.50")

    def test_cli_writes_the_workbook_prints_the_totals_and_reports_every_problem(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp, "bid-data.json")
            good.write_text(json.dumps(sample()), encoding="utf-8")
            out = Path(tmp, "bid-tab.xlsx")
            done = run(str(good), str(out))
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertIn("Lowest base bid: Northgate Drywall & Acoustics at $752,000", done.stdout)
            self.assertIn("Lowest complete leveled total: Prairie Wall & Ceiling Co. at $803,800", done.stdout)
            self.assertIn("- Northgate Drywall & Acoustics: $752,000 base + $55,800 plugs = $807,800 leveled, incomplete (1 gap without a plug)", done.stdout)
            self.assertIn("Flagged for review: 1 Addenda, 4 Suggested plug, 1 Needs a plug, 1 Not on scope sheet, 1 Check", done.stdout)
            self.assertEqual(out.read_bytes(), (SKILL / "samples" / "output-bid-tab.xlsx").read_bytes())

            bad = Path(tmp, "bad.json")
            bad.write_text(json.dumps(dict(sample(), asOf="Aug 22", bids=[])), encoding="utf-8")
            out.unlink()
            failed = run(str(bad), str(out))
            self.assertEqual(failed.returncode, 1)
            self.assertIn("2 problems:\n- asOf must be YYYY-MM-DD\n- at least two bids", failed.stderr)
            self.assertFalse(out.exists())
            self.assertEqual(run().returncode, 2)


if __name__ == "__main__":
    unittest.main()
