"""Reconcile the shipped sample proposal with its original staffing requirements.

This checks sample table arithmetic, not arbitrary agent prose. Fresh model
results use the semantic rubric in Task.md, without a heading/table gate.
"""
from datetime import date


def table_rows(text):
    return [[c.strip() for c in line.strip('|').split('|')]
            for line in text.splitlines() if line.startswith('|')]


def coverage_gaps(input_text, output_text):
    original = {}
    # Input assignment table has seven columns (id, employee, project, role, start, end, %).
    for row in table_rows(input_text):
        if len(row) == 7 and row[0].startswith('asg_'):
            original[row[0]] = dict(project=row[2].split()[0], role=row[3], start=row[4],
                                    end=row[5], allocation=float(row[6]))
    proposed = {key: dict(value) for key, value in original.items()}
    option_a = output_text.split('### Option A:', 1)[1].split('### Option B:', 1)[0]
    # Proposal tables have 10 columns (#, action, assignment, employee, project, role, start, end, %, reason).
    for row in table_rows(option_a):
        if len(row) == 10 and row[0].isdigit():
            key = row[2] if row[1] == 'Update' else 'new_' + row[0]
            proposed[key] = dict(project=row[4].split()[0], role=row[5], start=row[6],
                                 end=row[7], allocation=float(row[8]))
    if not original or proposed == original:
        raise ValueError('sample assignment/proposal rows missing')
    gaps = []
    for project in ('proj_0027', 'proj_0031'):
        before = [r for r in original.values() if r['project'] == project and r['role'] == 'Superintendent']
        after = [r for r in proposed.values() if r['project'] == project and r['role'] == 'Superintendent']
        boundaries = sorted({r[k] for r in before + after for k in ('start', 'end')})
        for a, b in zip(boundaries, boundaries[1:]):
            required = sum(r['allocation'] for r in before if r['start'] <= a < r['end'])
            retained = sum(r['allocation'] for r in after if r['start'] <= a < r['end'])
            if required != retained:
                gaps.append(dict(project=project, start=a, end=b, days=(date.fromisoformat(b)-date.fromisoformat(a)).days,
                                 required=required, retained=retained))
    return gaps
