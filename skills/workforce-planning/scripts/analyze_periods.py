#!/usr/bin/env python3
"""Analyze a normalized observed timeline; no network or mutations. See period-replay.md."""
import argparse
from datetime import date
import json
import math
from pathlib import Path


def day(value):
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError('dates must use YYYY-MM-DD')
    return parsed


def percent(value):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value < 0:
        raise ValueError('allocation must be a finite nonnegative number')
    return value


def analyze(data):
    start, end = map(day, data['window'])
    if end <= start:
        raise ValueError('window must have positive duration')
    threshold = data.get('bench_days', 30)
    if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 1:
        raise ValueError('bench_days must be a positive integer')
    needed = percent(data.get('required_allocation', 100))
    rows = []
    for row in data['periods']:
        a, b = day(row['start']), day(row['end'])
        if b <= a:
            raise ValueError('period must have positive duration')
        allocation = percent(row['utilization'])
        if not isinstance(row['time_off'], bool):
            raise ValueError('time_off must be boolean')
        if a < end and b > start:
            rows.append((max(a, start), min(b, end), allocation, row['time_off']))
    rows.sort()
    cursor = start
    gaps, intervals, bench = [], [], []
    run_start = run_end = None
    weighted = capped = 0

    def finish_run():
        if run_start is not None and (run_end - run_start).days >= threshold:
            bench.append({'start': str(run_start), 'end': str(run_end), 'days': (run_end - run_start).days})

    for a, b, allocation, off in rows:
        if a < cursor:
            raise ValueError('overlapping computed periods; resolve source data first')
        if a > cursor:
            gaps.append({'start': str(cursor), 'end': str(a)})
        if a != run_end or allocation != 0 or off:
            finish_run()
            run_start = run_end = None
        if allocation == 0 and not off:
            if run_start is None:
                run_start = a
            run_end = b
        days = (b - a).days
        weighted += days * allocation
        capped += days * min(100, allocation)
        capacity = 0 if off else max(0, 100 - allocation)
        intervals.append({'start': str(a), 'end': str(b), 'available_percent': capacity,
                          'meets_allocation': not off and capacity >= needed,
                          'overallocated': allocation > 100, 'time_off': off})
        cursor = b
    finish_run()
    if cursor < end:
        gaps.append({'start': str(cursor), 'end': str(end)})
    days = (end - start).days
    return {'employee_id': data['employee_id'], 'window': [str(start), str(end)],
            'provenance': data['provenance'], 'complete': not gaps, 'unknown_intervals': gaps,
            'bench': bench, 'capacity': intervals,
            'average_utilization': None if gaps else weighted / days,
            'capped_average_utilization': None if gaps else capped / days}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    try:
        result = analyze(json.loads(args.input.read_text()))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, f'Invalid timeline: {error}\n')
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
