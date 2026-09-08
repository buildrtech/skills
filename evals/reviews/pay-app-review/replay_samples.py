"""Replay both documented synthetic packages against frozen and revised scripts."""
from pathlib import Path
import json
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = Path('/tmp/skills-takeover-baseline-9a62032')
records = []
for name, memo, certified in [
    ('sample','skills/pay-app-review/samples/output-review-memo.md','323100'),
    ('harborview','evals/tasks/pay-app-review/harborview-app3/solution/reference-memo.md','822195'),
]:
    text = (BASE / memo).read_text()
    command = text.split('```\n')[1].split('```')[0].replace('\\\n',' ')
    args = shlex.split(command)[2:]
    args = [str(ROOT/'skills/pay-app-review'/x) if x.startswith('samples/') else
            str(ROOT/'evals/tasks/pay-app-review/harborview-app3/environment'/x.removeprefix('/app/')) if x.startswith('/app/') else x for x in args]
    outputs = {}
    for lane, directory in [('baseline',BASE),('revised',ROOT)]:
        invocation = [sys.executable,str(directory/'skills/pay-app-review/scripts/check_pay_app.py'),*args]
        if lane == 'revised':
            invocation += ['--prior-certified',certified]
        p = subprocess.run(invocation,capture_output=True,text=True)
        assert p.returncode == 1, p.stderr
        outputs[lane] = p.stdout
        (OUT/f'{name}-{lane}.md').write_text(p.stdout)
        records.append({'case':name,'lane':lane,'command':invocation,'exit':p.returncode})
    # All findings and monetary summary rows must match the frozen baseline.
    assert outputs['baseline'].split('Lines checked:')[0] == outputs['revised'].split('Lines checked:')[0]
    # Maintain documented executable examples and exact output excerpts.
    dest = ROOT/memo
    revised = dest.read_text()
    if '--prior-certified' not in revised.split('```')[1]:
        revised = revised.replace('--g702-previous '+certified,'--prior-certified '+certified+' --g702-previous '+certified,1)
    start = revised.index('## Findings (')
    end = revised.index('This output prepares a review.',start)
    end = revised.index('\n',end)
    revised = revised[:start]+outputs['revised'].rstrip()+revised[end:]
    dest.write_text(revised)
    if name == 'harborview':
        (ROOT/'evals/tasks/pay-app-review/harborview-app3/tests/fixtures/script-output.md').write_text(outputs['revised'])
(OUT/'sample-replay.json').write_text(json.dumps(records,indent=2)+'\n')
print('Both packages: findings and monetary summary rows identical to baseline; revised examples refreshed.')
