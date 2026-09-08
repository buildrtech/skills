"""Deterministic tests of the actual RFP verifier helpers (no model or mocks)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TASK = ROOT / 'evals/tasks/rfp-intake/brannock-fire-station-4'
sys.path.insert(0, str(TASK / 'tests'))
from common import rated_criteria_count

class RatedCriteriaTests(unittest.TestCase):
    def setUp(self):
        self.review = (TASK / 'solution/reference-intake-review.md').read_text()

    def test_reference_has_ten_rated_criteria(self):
        self.assertEqual(rated_criteria_count(self.review), 10)

    def test_alternate_headings_keep_ratings(self):
        self.assertEqual(rated_criteria_count(self.review.replace('Go/no-go scorecard', 'Criteria assessment')), 10)

    def test_blank_ratings_fail(self):
        import re
        self.assertEqual(rated_criteria_count(re.sub(r'\| (Favorable|Neutral|Unfavorable|Unknown) \|', '| |', self.review)), 0)

    def test_repeated_criterion_not_counted_twice(self):
        self.assertEqual(rated_criteria_count('| Schedule | Unfavorable | Winter work |\n' * 10), 1)

    def test_unrated_dates_do_not_count(self):
        self.assertEqual(rated_criteria_count('| Schedule | October 15, 2026 | IFB §3 |'), 0)

    def test_labeled_bullet_rating(self):
        self.assertEqual(rated_criteria_count('- **Scope fit:** Unknown — Confirm company experience.'), 1)

    def test_rating_needs_reason(self):
        self.assertEqual(rated_criteria_count('| Scope fit | Unknown | |'), 0)

if __name__ == '__main__':
    unittest.main()
