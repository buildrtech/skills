"""Real CLI regression checks; synthetic data, no MCP or model calls."""
import csv
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = Path(os.environ.get('PAY_APP_SCRIPT', ROOT / 'skills/pay-app-review/scripts/check_pay_app.py'))

class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.current = Path(self.tmp.name) / 'current.csv'
        self.prior = Path(self.tmp.name) / 'prior.csv'
        self.write(self.current, ['01','Concrete',1000,100,100,0,200,20,800,10])
        self.write(self.prior, ['01','Concrete',1000,0,100,0,100,10,900,10])

    def write(self, path, row):
        with path.open('w', newline='') as f:
            w = csv.writer(f)
            w.writerow('item description scheduled_value previous_completed this_period stored_materials total_completed percent_complete balance_to_finish retainage'.split())
            w.writerow(row)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), str(self.current), *args], capture_output=True, text=True)

    def test_missing_terms_stay_unknown(self):
        r = self.run_cli('--prior', str(self.prior))
        self.assertEqual(r.returncode, 0, r.stderr)
        for phrase in ['missing-contract-terms','missing-retainage-terms','missing-prior-certificate','| 5 | Retainage | n/a |']:
            self.assertIn(phrase, r.stdout)
        self.assertNotIn('| line-retainage |', r.stdout)

    def test_blank_amount_is_not_zero(self):
        self.write(self.current, ['01','Concrete',1000,100,'',0,100,10,900,10])
        r = self.run_cli('--contract-sum','1000')
        self.assertEqual(r.returncode, 2)
        self.assertIn('row 2', r.stderr)
        self.assertIn('this_period is blank', r.stderr)
        self.assertEqual(r.stdout, '')

    def test_nonfinite_csv_and_cli_are_input_errors(self):
        for value in ['NaN','Infinity','-Infinity']:
            with self.subTest(value=value):
                self.write(self.current, ['01','Concrete',1000,100,value,0,200,20,800,10])
                r = self.run_cli('--contract-sum','1000')
                self.assertEqual(r.returncode, 2)
                self.assertNotIn('Traceback', r.stderr)
                r = self.run_cli('--contract-sum',value)
                self.assertEqual(r.returncode, 2)
                self.assertNotIn('Traceback', r.stderr)

    def test_current_rate_does_not_recalculate_prior_certificate(self):
        r = self.run_cli('--contract-sum','1000','--change-orders','0','--retainage','5',
                         '--prior',str(self.prior),'--prior-certified','90','--g702-previous','90')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn('previous-certificates', r.stdout)
        self.assertIn('| 8 | Current payment due | 100.00 |', r.stdout)

    def test_wrong_line7_compares_to_independent_certificate(self):
        r = self.run_cli('--retainage','5','--prior-certified','80','--g702-previous','90')
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn('previous-certificates', r.stdout)
        self.assertIn('independently supplied cumulative prior certified amount is 80.00', r.stdout)
        self.assertIn('| 8 | Current payment due | 110.00 |', r.stdout)

    def test_as_submitted_math_runs_without_terms(self):
        r = self.run_cli('--g702-completed','200','--g702-retainage','10',
                         '--g702-earned','190','--g702-previous','90','--g702-due','99')
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn('| due-math |', r.stdout)
        self.assertIn('| 8 | Current payment due | n/a | 99.00 | n/a |', r.stdout)

    def test_invalid_rates_and_tolerance(self):
        for flag, value in [('--retainage','101'),('--stored-retainage','-1'),('--tolerance','-0.01')]:
            r = self.run_cli('--contract-sum','1000',flag,value)
            self.assertEqual(r.returncode, 2)
            self.assertNotIn('Traceback', r.stderr)

    def test_explicit_zero_terms_are_known(self):
        r = self.run_cli('--contract-sum','1000','--change-orders','0','--retainage','0','--prior-certified','0')
        self.assertEqual(r.returncode, 1)  # submitted retainage 10 conflicts with explicit zero
        self.assertIn('| line-retainage |', r.stdout)
        self.assertIn('| 8 | Current payment due | 200.00 |', r.stdout)
        self.assertNotIn('missing-retainage-terms', r.stdout)

if __name__ == '__main__':
    unittest.main(verbosity=2)
