#!/usr/bin/env python3
"""Reconcile supplied weekly staffing hours; never modify assignments."""
import json
import sys
from datetime import date
from decimal import Decimal


def hours(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError('Hours must be numeric')
    result = Decimal(str(value))
    if not result.is_finite() or result < 0:
        raise ValueError('Hours must be finite and nonnegative')
    return result


def indexed(rows):
    result = {}
    for row in rows:
        key = row['id']
        if not isinstance(key, str) or not key.strip() or key in result:
            raise ValueError('Missing or duplicate row ID')
        if date.fromisoformat(row['week']).isoformat() != row['week']:
            raise ValueError('Week must be an ISO date')
        result[key] = row
    return result


def reconcile(data):
    capacity = indexed(data['capacity'])
    demand = indexed(data['demand'])
    people = set()
    ledger = {}
    for key, row in capacity.items():
        person = row['person']
        if not isinstance(person, str) or not person.strip():
            raise ValueError('Person ID is required')
        identity = (person, row['week'])
        if identity in people:
            raise ValueError('Duplicate person/week capacity')
        people.add(identity)
        gross, absent, assigned = [hours(row[field]) for field in
                                  ('capacity_hours', 'unavailable_hours', 'assigned_hours')]
        if absent > gross:
            raise ValueError('Unavailable hours exceed capacity')
        usable = gross - absent
        ledger[key] = {'usable_hours': usable, 'assigned_hours': assigned,
                       'free_hours': max(Decimal(0), usable - assigned),
                       'overallocated_hours': max(Decimal(0), assigned - usable),
                       'proposed_hours': Decimal(0)}
    gaps = {key: {'initial_hours': hours(row['hours']),
                  'remaining_hours': hours(row['hours'])} for key, row in demand.items()}
    for proposal in data.get('proposals', []):
        person, need = proposal['capacity_id'], proposal['demand_id']
        if person not in capacity or need not in demand:
            raise ValueError('Unknown proposal reference')
        if capacity[person]['week'] != demand[need]['week']:
            raise ValueError('Proposal weeks must match')
        value = hours(proposal['hours'])
        if value > ledger[person]['free_hours'] or value > gaps[need]['remaining_hours']:
            raise ValueError('Proposal exceeds remaining capacity or demand')
        ledger[person]['free_hours'] -= value
        ledger[person]['proposed_hours'] += value
        gaps[need]['remaining_hours'] -= value
    return {'capacity': ledger, 'demand': gaps}


def main():
    try:
        with open(sys.argv[1], encoding='utf-8') as source:
            data = json.load(source, parse_float=Decimal)
        print(json.dumps(reconcile(data), default=lambda value: format(value, 'f'), indent=2))
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        print(f'Invalid staffing ledger: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
