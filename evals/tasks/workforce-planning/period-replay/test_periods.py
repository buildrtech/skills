"""Deterministic local replay, not MCP emulation or agent behavior evaluation."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / 'skills/workforce-planning/scripts/analyze_periods.py'
spec = importlib.util.spec_from_file_location('periods', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture(rows, window=('2028-01-01', '2028-03-01')):
    return {'employee_id': 'fixture_employee', 'provenance': 'synthetic fixture replay',
            'window': window, 'periods': [dict(start=a, end=b, utilization=u, time_off=t)
                                        for a, b, u, t in rows]}


class PeriodReplay(unittest.TestCase):
    def test_sample_dana_two_runs_not_225_day_bench(self):
        data = json.loads((Path(__file__).parent / 'sample-dana.json').read_text())
        result = module.analyze(data)
        self.assertEqual([x['days'] for x in result['bench']], [86, 132])
        self.assertEqual(result['capacity'][2]['available_percent'], 0)
        self.assertTrue(result['complete'])

    def test_leap_year_and_adjacent_zero_rows_merge(self):
        data = fixture([('2027-12-01', '2028-02-01', 0, False),
                        ('2028-02-01', '2028-04-01', 0, False)])
        self.assertEqual(module.analyze(data)['bench'],
                         [{'start': '2028-01-01', 'end': '2028-03-01', 'days': 60}])

    def test_time_off_breaks_bench_even_at_zero(self):
        data = fixture([('2028-01-01', '2028-01-31', 0, False),
                        ('2028-01-31', '2028-02-01', 0, True),
                        ('2028-02-01', '2028-03-01', 0, False)])
        result = module.analyze(data)
        self.assertEqual([x['days'] for x in result['bench']], [30])
        self.assertFalse(result['capacity'][1]['meets_allocation'])

    def test_missing_period_is_unknown_not_free(self):
        result = module.analyze(fixture([('2028-02-01', '2028-03-01', 0, False)]))
        self.assertFalse(result['complete'])
        self.assertIsNone(result['average_utilization'])
        self.assertEqual(result['unknown_intervals'], [{'start': '2028-01-01', 'end': '2028-02-01'}])
        self.assertEqual(result['bench'], [])

    def test_gap_breaks_zero_run(self):
        result = module.analyze(fixture([('2028-01-01', '2028-01-21', 0, False),
                                         ('2028-01-22', '2028-02-11', 0, False)]))
        self.assertEqual(result['bench'], [])
        self.assertEqual(len(result['unknown_intervals']), 2)

    def test_cap_before_weighting(self):
        result = module.analyze(fixture([('2028-01-01', '2028-01-31', 200, False),
                                         ('2028-01-31', '2028-03-01', 0, False)]))
        self.assertEqual(result['average_utilization'], 100)
        self.assertEqual(result['capped_average_utilization'], 50)
        self.assertTrue(result['capacity'][0]['overallocated'])

    def test_reject_duplicate_or_overlapping_computed_periods(self):
        with self.assertRaisesRegex(ValueError, 'overlapping'):
            module.analyze(fixture([('2028-01-01', '2028-02-01', 10, False)] * 2))

    def test_invalid_dates_flags_and_allocation_rejected(self):
        for row in [('2028-01-02', '2028-01-01', 0, False),
                    ('2028-01-01', '2028-02-01', -1, False),
                    ('2028-01-01', '2028-02-01', float('nan'), False),
                    ('2028-01-01', '2028-02-01', 0, 'false')]:
            with self.subTest(row=row), self.assertRaises(ValueError):
                module.analyze(fixture([row]))

    def test_partial_capacity_and_time_off(self):
        data = fixture([('2028-01-01', '2028-02-01', 50, False),
                        ('2028-02-01', '2028-03-01', 50, True)])
        data['required_allocation'] = 50
        result = module.analyze(data)
        self.assertEqual([x['meets_allocation'] for x in result['capacity']], [True, False])

    def test_empty_data_is_unknown(self):
        result = module.analyze(fixture([]))
        self.assertFalse(result['complete'])
        self.assertEqual(result['bench'], [])

    def test_sample_conserves_demand_and_negative_control_fails(self):
        from check_sample import coverage_gaps
        input_text = (ROOT / 'skills/workforce-planning/samples/input-request.md').read_text()
        output = (ROOT / 'skills/workforce-planning/samples/output-staffing-analysis.md').read_text()
        self.assertEqual(coverage_gaps(input_text, output), [])
        missing_residuals = '\n'.join(line for line in output.splitlines()
                                      if '(new residual demand)' not in line)
        gaps = coverage_gaps(input_text, missing_residuals)
        self.assertEqual(len(gaps), 2)
        self.assertTrue(all(g['required'] == 100 and g['retained'] == 50 and g['days'] == 47 for g in gaps))

    def test_real_cli(self):
        run = subprocess.run([sys.executable, str(SCRIPT), str(Path(__file__).parent / 'sample-dana.json')],
                             capture_output=True, text=True, check=True)
        self.assertEqual([x['days'] for x in json.loads(run.stdout)['bench']], [86, 132])


if __name__ == '__main__':
    unittest.main()
