# Local observed-period helper

Read before running `scripts/analyze_periods.py`. Python 3 standard library
only. Pass one employee per file, using computed periods from a discovered
live schema or explicitly supplied snapshot. This is a local normalization
contract, not an MCP schema. Preserve provenance in the input:

```json
{
  "employee_id": "synthetic_01",
  "provenance": {"mode": "synthetic fixture replay", "source": "provided.json"},
  "window": ["2028-01-01", "2028-02-01"],
  "required_allocation": 50,
  "bench_days": 30,
  "periods": [
    {"start": "2028-01-01", "end": "2028-02-01", "utilization": 0, "time_off": false}
  ]
}
```

All end dates are exclusive; all day counts are calendar days. Resolve
open-ended source dates against the window only if the source documents that
meaning. Each period must explicitly supply the time-off flag; incorporate
observed time-off boundaries before running if they arrive separately.
Missing intervals remain unknown. Overlapping computed periods are rejected,
not summed; source normalization must produce one observed timeline.

Output includes clipped consecutive bench runs, remaining capacity per period,
unknown intervals, observed utilization average, and the average with each
period capped at 100 before weighting. Both averages are null for incomplete
coverage. Time off breaks bench and has zero available capacity even with
zero utilization. Reported assignment utilization during time off still
contributes to the observed average; this is not an availability average.

The helper does not validate eligibility, headcount, certifications, demand
conservation, or proposed writes. Do those separately using data-model.md.
