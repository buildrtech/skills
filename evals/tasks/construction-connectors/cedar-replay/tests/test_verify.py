"""Verifier calibration, not agent behavior tests or live MCP proof."""
import copy
import json
import unittest
from pathlib import Path
from verify import grade

GOOD = json.loads(Path(__file__).with_name("known-good.json").read_text())


class VerifierTests(unittest.TestCase):
    def test_accepts_grounded_answer(self):
        self.assertTrue(all(grade(GOOD).values()))

    def test_accepts_order_and_extra_prose(self):
        answer = dict(reversed(list(GOOD.items())))
        answer["overdue_ids"] = ["19", "17", "18"]
        answer["explanation"] = "Permission denial leaves the second outcome unknown."
        self.assertTrue(all(grade(answer).values()))

    def test_scope_allows_context_but_requires_correct_identity(self):
        answer = copy.deepcopy(GOOD)
        answer["scope"].update(as_of="2026-11-06", timezone="America/Denver")
        self.assertTrue(all(grade(answer).values()))
        for key in GOOD["scope"]:
            with self.subTest(key=key):
                wrong = copy.deepcopy(answer)
                wrong["scope"][key] = "wrong-scope"
                self.assertFalse(grade(wrong)["scope"])
                del wrong["scope"][key]
                self.assertFalse(grade(wrong)["scope"])

    def test_link_context_preserves_exact_reference_and_record_set(self):
        answer = copy.deepcopy(GOOD)
        answer["confirmed_sheet_links"]["17"].update(
            label="S-210", current=True, evidence="Explicit external reference")
        self.assertTrue(all(grade(answer).values()))
        for key in GOOD["confirmed_sheet_links"]["17"]:
            wrong = copy.deepcopy(answer)
            wrong["confirmed_sheet_links"]["17"][key] = "wrong"
            self.assertFalse(grade(wrong)["confirmed_sheet_links"])
            del wrong["confirmed_sheet_links"]["17"][key]
            self.assertFalse(grade(wrong)["confirmed_sheet_links"])
        answer["confirmed_sheet_links"]["18"] = answer["confirmed_sheet_links"]["17"]
        self.assertFalse(grade(answer)["confirmed_sheet_links"])

    def test_rejects_substantive_errors(self):
        changes = [
            ("unique_records", 6),
            ("pagination_complete", False),
            ("overdue_ids", ["17", "18", "19", "20"]),
            ("missing_due_ids", []),
            ("outcomes", {"17": "verified", "18": "verified", "19": "verified"}),
            ("outcomes", {"17": "verified", "18": "failed", "19": "not_attempted"}),
            ("unresolved_sheet_links", []),
            ("live_writes_performed", 1),
            ("retry_permitted_by_request", True),
            ("mode", "live verified"),
            ("unique_records", True),
            ("overdue_ids", ["17", "18", "19", "19"]),
            ("overdue_ids", [{"id": "17"}]),
        ]
        for field, value in changes:
            with self.subTest(field=field, value=value):
                answer = copy.deepcopy(GOOD)
                answer[field] = value
                self.assertFalse(all(grade(answer).values()))

    def test_rejects_same_id_join_or_wrong_revision(self):
        for field, value in [("id", "17"), ("version", "v1"), ("project", "p4")]:
            with self.subTest(field=field):
                answer = copy.deepcopy(GOOD)
                answer["confirmed_sheet_links"]["17"][field] = value
                self.assertFalse(all(grade(answer).values()))

    def test_rejects_missing_or_malformed_answers(self):
        for answer in [None, [], {}, {"mode": "synthetic fixture replay"}]:
            self.assertFalse(all(grade(answer).values()))


if __name__ == "__main__":
    unittest.main()
