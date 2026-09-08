"""Run with uv --with jsonschema; validates actual generator fixture contracts."""
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator

skill=Path('skills/precon-pdf-templates')
for family in ['construction-budget-export','milestone-export','employee-resume']:
    schema=json.loads((skill/'schemas'/f'{family}.schema.json').read_text())
    Draft202012Validator.check_schema(schema)
    validator=Draft202012Validator(schema)
    data=json.loads((skill/'templates'/family/'field-ready-technical/sample-data.json').read_text())
    validator.validate(data)
    if family=='construction-budget-export':
        validator.validate(json.loads((skill/'samples/input-budget-data.json').read_text()))
        validator.validate(json.loads(Path('evals/tasks/precon-pdf-templates/alder-creek-budget/solution/reference-data.json').read_text()))
        for invalid in [None,0.1,'123',9007199254740992]:
            changed=copy.deepcopy(data); changed['divisions'][0]['totalCents']=invalid
            assert list(validator.iter_errors(changed)),invalid
        del data['totals']['grandTotalCents']
        assert list(validator.iter_errors(data))
    if family=='milestone-export':
        del data['summary']['constructionCostCents']
        assert list(validator.iter_errors(data))
    print(f'{family}: schema and sample validation passed; required money negatives rejected where applicable')
