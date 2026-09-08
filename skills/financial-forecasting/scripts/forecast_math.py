"""Calculate a normalized project snapshot; no MCP, network, or file writes."""
import argparse
from decimal import Decimal, InvalidOperation
import json


def calculate(row):
    for key in ('project_id', 'period_id'):
        if not isinstance(row.get(key), str) or not row[key].strip():
            raise ValueError(f'{key} must be a nonempty string')
    values = {}
    for key in ('contract_dollars', 'cost_to_date_cents', 'billed_to_date_cents', 'eac_cents'):
        try:
            value = Decimal(str(row[key]))
        except (KeyError, InvalidOperation):
            raise ValueError(f'{key} must be a finite number') from None
        if not value.is_finite():
            raise ValueError(f'{key} must be a finite number')
        values[key] = value if key == 'contract_dollars' else value / 100
    contract, cost, billed, eac = values.values()
    warnings = []
    completion = cost / eac if eac > 0 else None
    if completion is None:
        warnings.append('Nonpositive EAC: completion, earned revenue, and billing position unavailable')
    elif cost > eac:
        warnings.append('Cost exceeds EAC; completion is not capped')
    margin = (contract - eac) / contract * 100 if contract > 0 else None
    if margin is None:
        warnings.append('Nonpositive contract: margin unavailable')
    earned = completion * contract if completion is not None else None
    result = {
        'project_id': row['project_id'], 'period_id': row['period_id'],
        'contract_dollars': contract, 'cost_to_date_dollars': cost,
        'billed_to_date_dollars': billed, 'eac_dollars': eac,
        'completion_percent': completion * 100 if completion is not None else None,
        'earned_revenue_dollars': earned, 'margin_percent': margin,
        'estimated_profit_dollars': contract - eac,
        'over_under_dollars': billed - earned if earned is not None else None,
        'warnings': warnings,
    }
    return {key: float(value) if isinstance(value, Decimal) else value for key, value in result.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='Normalized local JSON snapshot; see forecast-model.md')
    args = parser.parse_args()
    try:
        with open(args.input) as source:
            row = json.load(source)
        if not isinstance(row, dict):
            raise ValueError('Input must be a JSON object')
        print(json.dumps(calculate(row), indent=2, allow_nan=False))
    except (OSError, ValueError) as error:
        parser.exit(2, f'error: {error}\n')


if __name__ == '__main__':
    main()
