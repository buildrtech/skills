import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from io import BytesIO
from pathlib import Path

SKILL = Path(__file__).resolve().parents[3] / "skills" / "bid-leveling"
SCRIPT = SKILL / "scripts" / "level.py"
sys.path.insert(0, str(SCRIPT.parent))
sys.dont_write_bytecode = True

from level import BidDataError, level, money, validate, workbook  # noqa: E402


def sample():
    return json.loads((SKILL / "samples" / "bid-data.json").read_text(encoding="utf-8"))


def pkg(**overrides):
    """A small package for rule-level tests: A excludes batts, C itemizes everything."""
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


def result(data, bidder):
    return next(r for r in level(validate(data))["results"] if r["bid"]["bidder"] == bidder)


def sheets(data):
    archive = zipfile.ZipFile(BytesIO(workbook(validate(data))))
    return {name: archive.read(name).decode("utf-8") for name in archive.namelist()}


def cell(sheet, ref):
    match = re.search(r'<c r="%s"[^>]*>(.*?)</c>' % ref, sheet)
    return match.group(1) if match else None


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
        self.assertEqual((by["Northgate"]["leveled"], by["Northgate"]["open"]), (80780000, 1))
        self.assertEqual((by["Prairie"]["leveled"], by["Prairie"]["open"]), (80380000, 0))
        self.assertEqual((by["Ridgeline"]["leveled"], by["Ridgeline"]["open"]), (82210000, 0))
        self.assertTrue(any("Confirm you received Addendum 2" in q for q in by["Northgate"]["questions"]))
        self.assertTrue(any("$781,000" in q for q in by["Ridgeline"]["questions"]))

    def test_suggested_plugs_use_the_highest_itemized_price_and_count_by_default(self):
        a = result(pkg(), "A")
        self.assertEqual(len(a["gaps"]), 1)
        self.assertEqual((a["gaps"][0]["amount"], a["gaps"][0]["carry"]), (20000, True))
        self.assertTrue(a["gaps"][0]["source"].startswith("Suggested: C itemized $200 "))
        self.assertEqual((a["leveled"], a["complete"]), (120000, True))

    def test_unclear_scope_or_scope_nobody_itemizes_stays_open(self):
        unclear = pkg()
        unclear["bids"][0]["scope"]["batts"] = {"status": "unclear", "quote": "Insulation per plans."}
        a = result(unclear, "A")
        self.assertEqual((a["gaps"][0]["amount"], a["gaps"][0]["carry"], a["complete"], a["leveled"]), (None, False, False, 100000))
        self.assertIn("Does your base bid include sound batts?", a["questions"][-1])

        nobody = pkg()
        for bid in nobody["bids"][1:]:
            bid["scope"]["batts"] = {"status": "included", "quote": "Batts."}
        self.assertIn("no other bid itemizes", result(nobody, "A")["gaps"][0]["source"])

    def test_entered_plugs_replace_suggestions_and_need_a_gap_and_a_source(self):
        a = result(pkg(plugs=[{"bidder": "A", "scope": "batts", "amount": 175.5, "source": "GC budget line 0921"}]), "A")
        self.assertEqual((a["gaps"][0]["amount"], a["leveled"]), (17550, 117550))
        self.assertEqual(a["gaps"][0]["source"], "Entered: GC budget line 0921")

        bad = pkg(plugs=[
            {"bidder": "B", "scope": "batts", "amount": 10, "source": "x"},
            {"bidder": "A", "scope": "batts", "amount": 10, "source": ""},
            {"bidder": "Z", "scope": "batts", "amount": 10, "source": "x"},
        ])
        with self.assertRaises(BidDataError) as raised:
            validate(bad)
        for text in ("nothing to plug", "say where the figure came from", 'no bid from "Z"'):
            self.assertIn(text, str(raised.exception))

    def test_validation_refuses_incomplete_or_uncited_extractions(self):
        data = pkg()
        del data["bids"][0]["scope"]["framing"]
        data["bids"][1]["scope"]["batts"] = {"status": "excluded"}
        data["bids"][2]["scope"]["framing"] = {"status": "omitted", "amount": 5}
        data["bids"][2]["total"] = 10.005
        data["bids"].append(copy.deepcopy(data["bids"][1]))
        with self.assertRaises(BidDataError) as raised:
            validate(data)
        for text in ('no entry for scope line "framing"', "B / batts: quote the bid's words", "only included lines carry an amount",
                     "C: total must be", 'bidder "B" must be named and unique'):
            self.assertIn(text, str(raised.exception))
        with self.assertRaisesRegex(BidDataError, "at least two bids"):
            validate(pkg(bids=pkg()["bids"][:1]))
        true_total = pkg()
        true_total["bids"][0]["total"] = True
        with self.assertRaisesRegex(BidDataError, "A: total must be"):
            validate(true_total)

    def test_missing_or_unstated_addenda_are_asked_about(self):
        data = pkg(addenda=[1, 2])
        data["bids"][2]["addenda"] = None
        self.assertRegex(result(data, "A")["questions"][0], r"acknowledges Addendum 1\. Confirm you received Addendum 2")
        self.assertIn("doesn't say which addenda", result(data, "C")["questions"][0])

    def test_totals_are_formulas_over_the_plugs_sheet_with_cached_values(self):
        data = pkg()
        data["bids"][0]["scope"]["framing"] = {"status": "unclear", "quote": "Framing & board."}
        files = sheets(data)
        self.assertIn('fullCalcOnLoad="1"', files["xl/workbook.xml"])
        self.assertRegex(files["xl/workbook.xml"], r'name="Leveled totals".*name="Scope".*name="Plugs".*name="Questions"')
        totals = files["xl/worksheets/sheet1.xml"]
        self.assertEqual(cell(totals, "C2"), "<f>SUMIFS(Plugs!$D:$D,Plugs!$A:$A,$A2,Plugs!$F:$F,&quot;Yes&quot;)</f><v>200</v>")
        self.assertEqual(cell(totals, "D2"), "<f>B2+C2</f><v>1200</v>")
        self.assertRegex(cell(totals, "E2"), r"COUNTIFS.*<v>1</v>$")
        self.assertRegex(cell(totals, "F2"), r"<v>Incomplete</v>$")
        # A is incomplete, so the lowest complete is C at $1,100, not A at $1,200.
        self.assertRegex(cell(totals, "B8"), r"_xlfn\.MINIFS.*<v>C</v>$")
        self.assertRegex(cell(totals, "D8"), r"<v>1100</v>$")
        plugs = files["xl/worksheets/sheet3.xml"]
        self.assertIn("Unclear: &quot;Framing &amp; board.&quot;", plugs)
        self.assertIn("Yes", cell(plugs, "F3"))

    def test_no_complete_bid_is_reported_as_none(self):
        data = pkg()
        for bid in data["bids"]:
            bid["scope"]["batts"] = {"status": "unclear", "quote": "Insulation?"}
        self.assertIsNone(level(validate(data))["lowest_complete"])
        self.assertRegex(cell(sheets(data)["xl/worksheets/sheet1.xml"], "B8"), r"<v>None complete</v>$")

    def test_money_formatting(self):
        self.assertEqual(money(80380000), "$803,800")
        self.assertEqual(money(17550), "$175.50")
        self.assertEqual(money(-950), "-$9.50")

    def test_cli_writes_the_workbook_prints_json_and_reports_every_problem(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp, "bid-data.json")
            good.write_text(json.dumps(sample()), encoding="utf-8")
            out = Path(tmp, "bid-tab.xlsx")
            done = run(str(good), str(out))
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertIn("Lowest complete: Prairie Wall & Ceiling Co. at $803,800", done.stderr)
            self.assertEqual(out.read_bytes(), (SKILL / "samples" / "output-bid-tab.xlsx").read_bytes())

            summary = json.loads(run(str(good), "--json").stdout)
            self.assertEqual(summary["lowestComplete"], "Prairie Wall & Ceiling Co.")
            self.assertEqual(summary["results"][0]["leveled"], 807800)

            bad = Path(tmp, "bad.json")
            bad.write_text(json.dumps(dict(sample(), asOf="Aug 22", bids=[])), encoding="utf-8")
            failed = run(str(bad), str(out))
            self.assertEqual(failed.returncode, 1)
            self.assertIn("2 problems:\n- asOf must be YYYY-MM-DD\n- at least two bids", failed.stderr)
            self.assertEqual(run().returncode, 2)


if __name__ == "__main__":
    unittest.main()
