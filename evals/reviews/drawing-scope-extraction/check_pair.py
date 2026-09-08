"""Private checks for the unfamiliar Juniper task; never copied to evaluators."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

REVIEW = Path(__file__).resolve().parent
BASE = REVIEW / 'paired'
REPO = REVIEW.parents[2]
SCRIPT_PATH = 'skills/drawing-scope-extraction/scripts/scope_list.py'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--baseline-root', type=Path, default=os.environ.get('DRAWING_BASELINE_ROOT'),
                    help='Baseline repository root; also accepts DRAWING_BASELINE_ROOT. Defaults to git 9a62032.')
args = parser.parse_args()
if args.baseline_root:
    baseline_command = [sys.executable, str(args.baseline_root / SCRIPT_PATH)]
else:
    baseline = subprocess.run(['git', 'show', f'9a62032:{SCRIPT_PATH}'], cwd=REPO,
                              capture_output=True, text=True)
    if baseline.returncode:
        parser.error('git baseline 9a62032 unavailable; pass --baseline-root or DRAWING_BASELINE_ROOT with an archived baseline checkout')
    # The renderer is a standalone standard-library script; execute the exact
    # git object without requiring a persistent /tmp checkout.
    baseline_command = [sys.executable, '-c', baseline.stdout]
COMMANDS = {
    'baseline': baseline_command,
    'revised': [sys.executable, str(REPO / SCRIPT_PATH)],
}
results = {}
for lane in ('baseline', 'revised'):
    root = BASE / lane
    data = json.loads((root / 'output/candidates.json').read_text())
    candidates = {c['id']: c for c in data['candidates']}
    sheets = {e['source']: e for e in data['coverage_ledger'] if e['kind'] == 'sheet'}
    source = (root / 'input/sheet-index.md').read_text()
    rendered = subprocess.run([*COMMANDS[lane], str(root / 'output/candidates.json')], capture_output=True, text=True)
    checks = {
        'backing_included': candidates['cand-001']['decision'] == 'include',
        'explicit_shelves_included': candidates['cand-002']['decision'] == 'include',
        'dependent_hardware_review': candidates['cand-003']['decision'] == 'review',
        'hardware_primary_corrected': candidates['cand-003']['sheet_number'] == 'A-110',
        'owner_sensors_excluded': candidates['cand-004']['decision'] == 'exclude' and candidates['cand-004']['support_level'] == 'by_others',
        'four_real_sheets_with_unreadable_schedule': set(sheets) == {'G-010','A-110','A-610','M-110'} and sheets['A-610']['status'] == 'unreadable',
        'quotes_in_primary_sheet_text': all(c['quote'] in source.split('## '+c['sheet_number']+'\n',1)[1].split('\n## ',1)[0] for c in candidates.values()),
        'valid_output_from_bundled_renderer': rendered.returncode == 0 and rendered.stdout == (root / 'output/scope-list.md').read_text(),
    }
    results[lane] = dict(checks=checks, passed=sum(checks.values()), total=len(checks), decisions={k:v['decision'] for k,v in candidates.items()})
print(json.dumps(results,indent=2))
