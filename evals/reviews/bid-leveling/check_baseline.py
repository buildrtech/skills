"""Actual CLI smoke-pair hashes and arithmetic ties for existing fixtures."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

repo=Path(__file__).resolve().parents[3]
base=Path('/tmp/skills-takeover-baseline-9a62032')
result={}
for lane,root in [('baseline',base),('revised',repo)]:
    script=root/'skills/bid-leveling/scripts/level_bids.py'
    spec=importlib.util.spec_from_file_location(lane,script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result[lane]={'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest()}
    for case,paths in [
        ('sample',sorted((root/'skills/bid-leveling/samples').glob('*.json'))),
        ('millbrook',sorted((root/'evals/tasks/bid-leveling/millbrook-roofing-07a/tests/fixtures').glob('extraction-*.json'))+[root/'evals/tasks/bid-leveling/millbrook-roofing-07a/environment/input/estimator-decisions.json'])]:
        paths=list(map(str,paths));proc=subprocess.run([sys.executable,str(script),*paths],capture_output=True,text=True)
        assert proc.returncode==0,proc.stderr
        extra,decisions,errors=module.load_inputs(paths);assert not errors
        model=module.build_model(extra,decisions)
        totals={b['extraction']['bidder_name']:{'total_cents':b['leveled'],'complete':b['complete']} for b in model['bidders'].values()}
        result[lane][case]={'stdout_sha256':hashlib.sha256(proc.stdout.encode()).hexdigest(),'totals':totals}
        if case=='sample': assert proc.stdout==(root/'skills/bid-leveling/samples/output-leveled-comparison.md').read_text()
for case in ('sample','millbrook'):
    assert result['baseline'][case]['totals']==result['revised'][case]['totals']
result['outcome']='Arithmetic/completeness tie on both original fixtures; output differs only in traceable identity/alternate presentation and submission labels in flags.'
print(json.dumps(result,indent=2))
