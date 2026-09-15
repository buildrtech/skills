import copy
import importlib.util
import json
from pathlib import Path
import unittest
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[4]
SKILL = ROOT / 'skills/workforce-planning'
spec = importlib.util.spec_from_file_location('capacity', SKILL / 'scripts/capacity.py')
capacity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capacity)

class CapacityTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((SKILL / 'samples/input-week.json').read_text())

    def test_proposal_reconciles_and_preserves_overload(self):
        before = copy.deepcopy(self.data)
        result = capacity.reconcile(self.data)
        self.assertEqual(result['demand']['d-library']['remaining_hours'], Decimal(4))
        self.assertEqual(result['capacity']['c-cam']['overallocated_hours'], Decimal(4))
        self.assertEqual(sum(r['proposed_hours'] for r in result['capacity'].values()), Decimal(20))
        self.assertEqual(self.data, before)

    def test_repeated_fill_cannot_reuse_capacity(self):
        self.data['proposals'].append(self.data['proposals'][0])
        with self.assertRaises(ValueError): capacity.reconcile(self.data)

    def test_cannot_fill_more_than_remaining_demand(self):
        self.data['demand'][0]['hours'] = 10
        with self.assertRaises(ValueError): capacity.reconcile(self.data)

    def test_duplicate_people_and_ids_rejected(self):
        for change_id in (False, True):
            data = copy.deepcopy(self.data)
            row = copy.deepcopy(data['capacity'][0])
            if change_id: row['id'] = 'duplicate-person'
            data['capacity'].append(row)
            with self.assertRaises(ValueError): capacity.reconcile(data)

    def test_unknown_refs_and_other_weeks_rejected(self):
        for key, value in [('capacity_id', 'missing'), ('demand_id', 'missing')]:
            data = copy.deepcopy(self.data); data['proposals'][0][key] = value
            with self.assertRaises(ValueError): capacity.reconcile(data)
        self.data['demand'][0]['week'] = '2026-09-28'
        with self.assertRaises(ValueError): capacity.reconcile(self.data)

    def test_bad_hours_and_missing_capacity_rejected(self):
        for value in [True, -1, float('nan'), float('inf'), '40', None]:
            data = copy.deepcopy(self.data);data['capacity'][0]['capacity_hours'] = value
            with self.assertRaises(ValueError): capacity.reconcile(data)
        del self.data['capacity'][0]['capacity_hours']
        with self.assertRaises(KeyError): capacity.reconcile(self.data)

    def test_absence_and_decimal_hours(self):
        self.data['capacity'][0]['unavailable_hours'] = 41
        with self.assertRaises(ValueError): capacity.reconcile(self.data)
        self.data['capacity'][0]['unavailable_hours'] = Decimal('8.25')
        self.data['proposals'][0]['hours'] = Decimal('7.75')
        result = capacity.reconcile(self.data)
        self.assertEqual(result['demand']['d-library']['remaining_hours'], Decimal('4.25'))

if __name__ == '__main__': unittest.main()
