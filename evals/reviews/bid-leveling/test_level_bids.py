"""Deterministic synthetic fixture replay; no model or MCP calls.
Run: python3 -m unittest discover -s evals/reviews/bid-leveling -p 'test_*.py' -v
"""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / 'skills/bid-leveling/scripts/level_bids.py'
BASELINE = Path('/tmp/skills-takeover-baseline-9a62032/skills/bid-leveling/scripts/level_bids.py')
spec = importlib.util.spec_from_file_location('level_bids', SCRIPT)
level = importlib.util.module_from_spec(spec)
spec.loader.exec_module(level)


def bid(sid='a', company='Alder Masonry', total=1000000):
    return dict(submission_id=sid, bidder_name=company, source_files=[sid+'.txt'],
                document_role='quote', trade_scope='Masonry', total_bid_amount_in_cents=total,
                scopes_of_work=[dict(scope_key='wall', scope='Wall', evidence_ref='E')],
                excluded_scopes=[dict(scope_key='cleanup', scope='Cleanup', status='excluded', evidence_ref='E')],
                alternate_lines=[dict(alternate_key='finish', label='Stone finish', printed_label='Alt 1',
                                      kind='add', solicited=True, amount_in_cents=20000, evidence_ref='E')],
                unit_price_lines=[], priced_qualifications=[], review_items=[], qualifications=[],
                evidence=[dict(ref='E', source_file=sid+'.txt', location='quote',
                               quote='Wall included, cleanup excluded; stone finish add $200.')])


def run_cli(submissions, decisions=None, script=SCRIPT, extra=()):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp)/'bids.json'; path.write_text(json.dumps(submissions))
        args = [sys.executable, str(script), str(path)]
        if decisions is not None:
            path = Path(tmp)/'decisions.json'; path.write_text(json.dumps(decisions)); args.append(str(path))
        return subprocess.run(args+list(extra), capture_output=True, text=True)


class BidLevelingTests(unittest.TestCase):
    def assert_invalid(self, submissions, decisions=None, message=''):
        result = run_cli(submissions, decisions)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertNotIn('Traceback', result.stderr)
        self.assertIn(message, result.stderr)

    def test_same_company_submissions_and_targeted_plug(self):
        a, b = bid(), bid('b', total=900000)
        decisions={'plugs':[dict(submission_id='b', scope_key='cleanup', amount_in_cents=30000, source='Estimator S, estimate line 8') ]}
        result=run_cli([a,b],decisions)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('Alder Masonry [a]', result.stdout)
        self.assertIn('Alder Masonry [b] at $9,300', result.stdout)
        self.assertIn('$10,000 (incomplete)', result.stdout)
        # Same facts on the old schema demonstrate the actual dropped submission.
        old=run_cli([a,b],script=BASELINE)
        self.assertEqual(old.returncode,0)
        self.assertIn('only the first was used',old.stdout)
        self.assertNotIn('$9,000',old.stdout)

    def test_duplicate_submission_is_rejected(self):
        self.assert_invalid([bid(),bid()],message='duplicate submission_id')

    def test_printed_alternate_reconciliation(self):
        a,b=bid(),bid('b','Birch Masonry')
        b['alternate_lines'][0]['printed_label']='Option B'
        self.assert_invalid([a,b],message='printed labels differ')
        for item in [a,b]: item['alternate_lines'][0]['reconciliation_note']='Package addendum C maps stone finish to Option B / Alt 1.'
        result=run_cli([a,b]);self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('Option B (E)',result.stdout);self.assertIn('Alt 1 (E)',result.stdout)
        self.assertIn('mapped: Package addendum C',result.stdout)
        self.assertIn('$10,000 (incomplete)',result.stdout)

    def test_duplicate_alternate_is_rejected(self):
        a=bid();a['alternate_lines'].append(copy.deepcopy(a['alternate_lines'][0]))
        self.assert_invalid([a],message='duplicate row key')

    def test_duplicate_alternate_with_scope_namespace_collision(self):
        a=bid()
        a['alternate_lines'][0]['alternate_key']='wall'
        a['alternate_lines'].append(copy.deepcopy(a['alternate_lines'][0]))
        self.assert_invalid([a],message='duplicate row key')

    def test_conflicting_alternate_scope_or_kind_is_rejected(self):
        for field,value in [('label','Brick finish'),('kind','replace')]:
            with self.subTest(field=field):
                a,b=bid(),bid('b','Birch');b['alternate_lines'][0][field]=value
                self.assert_invalid([a,b],message='conflicting scope label or kind')

    def test_voluntary_alternates_are_isolated(self):
        a,b=bid(),bid('b','Birch')
        for item in [a,b]: item['alternate_lines'][0]['solicited']=False
        b['alternate_lines'][0]['label']='Brick finish'
        result=run_cli([a,b]);self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.count('| no (bidder-proposed) |'),2)

    def test_alternate_sign_and_null(self):
        a=bid();a['alternate_lines'][0]['kind']='deduct'
        self.assert_invalid([a],message='sign disagrees')
        a['alternate_lines'][0]['amount_in_cents']=None
        self.assertIn('priced: not stated',run_cli([a]).stdout)

    def test_duplicate_plugs_never_double_count(self):
        p=dict(submission_id='a',scope_key='cleanup',amount_in_cents=50000,source='Estimator S estimate line 8')
        self.assert_invalid([bid()],{'plugs':[p,p]},'duplicate plug')

    def test_bad_decisions_fail_before_arithmetic(self):
        for value in ['100',None,True]:
            self.assert_invalid([bid()],{'plugs':[dict(submission_id='a',scope_key='cleanup',amount_in_cents=value,source='Estimator')]},'must be an integer')
        for decisions in [{'plugs':7},{'plugs':[7]},{'plugs':[{'submission_id':[]}]}]:
            self.assert_invalid([bid()],decisions)

    def test_missing_or_invalid_evidence(self):
        for change in ['missing','unknown','duplicate','source']:
            a=bid()
            if change=='missing': del a['alternate_lines'][0]['evidence_ref']
            if change=='unknown': a['alternate_lines'][0]['evidence_ref']='NOPE'
            if change=='duplicate': a['evidence'].append(a['evidence'][0])
            if change=='source': a['evidence'][0]['source_file']='unknown.pdf'
            self.assert_invalid([a],message='evidence')

    def test_scope_conflict_cannot_hide_a_gap(self):
        a,b=bid(),bid('b','Birch');b['excluded_scopes'][0]['row_class']='outside_scope'
        self.assert_invalid([a,b],message='conflicting row_class')
        a['scopes_of_work'].append(dict(scope_key='cleanup',evidence_ref='E'))
        self.assert_invalid([a],message='duplicate row key')

    def test_sample_and_existing_fixture_arithmetic(self):
        for root,decisions,expected in [
            (REPO/'skills/bid-leveling/samples','input-estimator-decisions.json',[89570000,83370000,82930000]),
            (REPO/'evals/tasks/bid-leveling/millbrook-roofing-07a/tests/fixtures','../../environment/input/estimator-decisions.json',[61470000,58085000,61925000])]:
            paths=sorted(root.glob('*extraction-*.json'))+[root/decisions]
            extra,d,errors=level.load_inputs([str(p) for p in paths]);self.assertEqual(errors,[])
            self.assertEqual(level.validate_reconciliation(extra),[])
            model=level.build_model(extra,d)
            self.assertEqual([b['leveled'] for b in model['bidders'].values()],expected)
            self.assertEqual(sum(len(b['unresolved']) for b in model['bidders'].values()),1)

    def test_xlsx_same_submission_and_alternate_tables(self):
        try: from openpyxl import load_workbook
        except ImportError: self.skipTest('optional openpyxl not installed')
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'comparison.xlsx'
            result=run_cli([bid(),bid('b',total=900000)],extra=['--xlsx',str(path)])
            self.assertEqual(result.returncode,0,result.stderr)
            workbook=load_workbook(path)
            self.assertEqual(workbook['Summary']['A5'].value,'Alder Masonry [a]')
            self.assertEqual(workbook['Summary']['A6'].value,'Alder Masonry [b]')
            self.assertIn('Alt 1 (E)',workbook['Alternates']['D2'].value)

if __name__=='__main__': unittest.main()
