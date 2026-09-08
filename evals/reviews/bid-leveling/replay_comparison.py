"""Preserve actual baseline/revised CLI outputs for the synthetic defect cases."""
import copy
import json
from pathlib import Path
from test_level_bids import bid, run_cli, SCRIPT, BASELINE

root=Path(__file__).resolve().parent/'comparison';root.mkdir(exist_ok=True)
a,b=bid(),bid('b',total=900000)
cases={'same-company':([a,b],None)}
a,b=bid(),bid('b','Birch');b['alternate_lines'][0]['printed_label']='Option B'
cases['unreconciled-labels']=([a,b],None)
a=bid();a['alternate_lines'].append({**a['alternate_lines'][0],'amount_in_cents':99000})
cases['duplicate-alternate']=([a],None)
p=dict(submission_id='a',scope_key='cleanup',amount_in_cents=50000,source='Estimator S estimate line 8')
cases['duplicate-plug']=([bid()],{'plugs':[p,p]})
results={}
for name,(bids,decisions) in cases.items():
    results[name]={}
    (root/(name+'-input.json')).write_text(json.dumps({'submissions':bids,'decisions':decisions},indent=2)+'\n')
    for lane,script in [('baseline',BASELINE),('revised',SCRIPT)]:
        d=copy.deepcopy(decisions)
        if lane=='baseline' and d:
            lookup={b['submission_id']:b['bidder_name'] for b in bids}
            d['plugs'] = [{**{k:v for k,v in item.items() if k != 'submission_id'}, 'bidder_name':lookup[item['submission_id']]} for item in d['plugs']]
        result=run_cli(bids,d,script)
        if result.stdout: (root/f'{name}-{lane}.md').write_text(result.stdout)
        if result.stderr: (root/f'{name}-{lane}.stderr').write_text(result.stderr)
        results[name][lane]={'exit':result.returncode,'stdout':f'{name}-{lane}.md' if result.stdout else None,'stderr':f'{name}-{lane}.stderr' if result.stderr else None}
(root/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
