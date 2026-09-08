"""Deterministic synthetic replay; does not test live tools or agent behavior."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / 'skills/financial-forecasting/scripts/forecast_math.py'
spec = importlib.util.spec_from_file_location('forecast_math', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
FIXTURE = Path(__file__).with_name('input.json')


class ForecastMathTest(unittest.TestCase):
    def setUp(self):
        self.row = json.loads(FIXTURE.read_text())

    def test_actual_cli_with_independent_expected_values(self):
        run = subprocess.run([sys.executable, str(SCRIPT), str(FIXTURE)], text=True, capture_output=True, check=True)
        result = json.loads(run.stdout)
        expected = {'completion_percent': 45, 'earned_revenue_dollars': 1125000,
                    'margin_percent': 16, 'over_under_dollars': -45000,
                    'estimated_profit_dollars': 400000, 'cost_to_date_dollars': 945000}
        for key, value in expected.items():
            self.assertEqual(result[key], value)
        self.assertEqual(result['period_id'], self.row['period_id'])

    def test_existing_sample_harbor_arithmetic(self):
        self.row.update(contract_dollars=12400000, cost_to_date_cents=691920000,
                        billed_to_date_cents=775000000, eac_cents=1153200000)
        result = module.calculate(self.row)
        self.assertEqual((result['completion_percent'], result['margin_percent'], result['over_under_dollars']), (60, 7, 310000))

    def test_nonpositive_eac_preserves_input_and_marks_undefined(self):
        for eac in (0, -1):
            self.row['eac_cents'] = eac
            result = module.calculate(self.row)
            for key in ('completion_percent', 'earned_revenue_dollars', 'over_under_dollars'):
                self.assertIsNone(result[key])
            self.assertEqual(result['cost_to_date_dollars'], 945000)
            self.assertTrue(result['warnings'])

    def test_zero_contract_and_uncapped_completion(self):
        self.row.update(contract_dollars=0, eac_cents=90000000)
        result = module.calculate(self.row)
        self.assertIsNone(result['margin_percent'])
        self.assertEqual(result['completion_percent'], 105)
        self.assertEqual(len(result['warnings']), 2)

    def test_missing_nonfinite_and_boolean_amounts_rejected(self):
        for value in (None, True, 'NaN', 'Infinity', 'not money'):
            self.row['eac_cents'] = value
            with self.assertRaises(ValueError):
                module.calculate(self.row)
        del self.row['eac_cents']
        with self.assertRaises(ValueError):
            module.calculate(self.row)

    def test_ids_required(self):
        self.row['period_id'] = ''
        with self.assertRaises(ValueError):
            module.calculate(self.row)


if __name__ == '__main__':
    unittest.main()
