"""Deterministic CLI checks; SCOPE_SCRIPT selects the preserved baseline."""
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = Path(os.environ.get('SCOPE_SCRIPT', ROOT / 'skills/drawing-scope-extraction/scripts/scope_list.py'))
SAMPLE = ROOT / 'skills/drawing-scope-extraction/samples/input-candidates.json'


class ScopeListTest(unittest.TestCase):
    def run_data(self, data):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'candidates.json'
            source.write_text(json.dumps(data))
            return subprocess.run(['python3', str(SCRIPT), str(source)], capture_output=True, text=True)

    def setUp(self):
        self.data = json.loads(SAMPLE.read_text())

    def test_sample_and_oracle_render(self):
        for path in [SAMPLE, ROOT / 'evals/tasks/drawing-scope-extraction/larkspur-ridge-ops-addition/tests/fixtures/reference-candidates.json']:
            result = self.run_data(json.loads(path.read_text()))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('## Coverage ledger', result.stdout)

    def test_unreadable_primary_cannot_be_included(self):
        for status in ['unreadable', 'not_reviewed']:
            with self.subTest(status=status):
                data = copy.deepcopy(self.data)
                data['coverage_ledger'][1]['status'] = status
                result = self.run_data(data)
                self.assertEqual(result.returncode, 1)
                self.assertIn('reviewed primary sheet', result.stderr)
                self.assertEqual(result.stdout, '')

    def test_malformed_optional_fields_have_actionable_errors(self):
        for group, field, value in [('candidates', 'related_sheets', [dict()]), ('coverage_ledger', 'candidate_ids', 5), ('rfis', 'candidate_ids', [dict()]), ('coverage_ledger', 'title', 1)]:
            with self.subTest(group=group, field=field):
                data = copy.deepcopy(self.data)
                data[group][0][field] = value
                result = self.run_data(data)
                self.assertEqual(result.returncode, 1)
                self.assertIn(field, result.stderr)
                self.assertNotIn('Traceback', result.stderr)
                self.assertEqual(result.stdout, '')

    def test_boolean_sheet_count_and_bad_id_rejected(self):
        data = {'set_name': 'Synthetic one-sheet excerpt', 'sheet_count': True, 'candidates': [], 'coverage_ledger': [self.data['coverage_ledger'][0]]}
        data['coverage_ledger'][0]['candidate_ids'] = []
        self.assertEqual(self.run_data(data).returncode, 1)
        self.data['candidates'][0]['id'] = 'arbitrary'
        self.data['coverage_ledger'][1]['candidate_ids'][0] = 'arbitrary'
        self.assertIn('id must match', self.run_data(self.data).stderr)

    def test_weak_support_remains_rejected(self):
        for support in ['inferred', 'reference_only', 'by_others']:
            with self.subTest(support=support):
                self.data['candidates'][0]['support_level'] = support
                self.assertEqual(self.run_data(self.data).returncode, 1)

    def test_readable_primary_can_have_unreadable_related_sheet(self):
        self.data['candidates'][0]['related_sheets'] = ['P-101']
        self.assertEqual(self.run_data(self.data).returncode, 0)


if __name__ == '__main__':
    unittest.main()
