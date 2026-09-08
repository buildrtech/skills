"""Deterministic parser and demonstration checks; no agent behavior claims."""
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "evals/tasks/rfi-drafter/sable-creek-rfi-023/tests"))
from common import section, dates, log_rows


class RfiRegressions(unittest.TestCase):
    def test_equivalent_sections_keep_boundaries(self):
        text = "## Clarification requested\nCould you confirm strength?\n## Proposed resolution\nProposal\n## Impact\nPotential"
        self.assertEqual(section(text, "Question").strip(), "Could you confirm strength?")
        self.assertEqual(section(text, "Suggested resolution").strip(), "Proposal")

    def test_no_section_means_no_credit(self):
        self.assertEqual(section("The question remains open.", "Question"), "")
        self.assertEqual(section("## Impact\nPotential", "Suggested resolution"), "")

    def test_quoted_wrapped_source_date(self):
        self.assertEqual(dates("> Monday, October 19,\n> 2026."), {"2026-10-19"})
        self.assertNotIn("2026-10-20", dates("> Monday, October 19,\n> 2026."))

    def test_demo_log_dates_match_source_arithmetic(self):
        text = (ROOT / "skills/rfi-drafter/samples/output-rfi.md").read_text()
        row = log_rows(text, "RFI-047")[0]
        self.assertEqual(len(row), 11)
        self.assertEqual(dates(row[5]), {(date(2026, 9, 25) - timedelta(days=7)).isoformat()})
        current = date(2026, 9, 8)
        for _ in range(10):
            current += timedelta(days=1)
            while current.weekday() >= 5:
                current += timedelta(days=1)
        self.assertEqual(current, date(2026, 9, 22))
        self.assertIn("September 22", text)


if __name__ == "__main__":
    unittest.main()
