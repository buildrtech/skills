"""Replay identical controls through baseline and revised RFP verifiers.

Set UV_TOOL_DIR and UV_CACHE_DIR to writable /tmp directories before running.
Only fixture replay occurs; this does not launch a model or call remote APIs.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
ROOT = Path(__file__).resolve().parents[3]
TASK_PATH = Path('evals/tasks/rfp-intake/brannock-fire-station-4')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-root', type=Path,
                        default=Path('/tmp/skills-takeover-baseline-9a62032'))
    args = parser.parse_args()
    baseline = args.baseline_root / TASK_PATH
    if not (baseline / 'tests/reward.toml').is_file():
        parser.error(f'Baseline task not found: {baseline}')
    spec = importlib.util.spec_from_file_location(
        'fixture_runner', ROOT / 'evals/scripts/check_fixtures.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    task = ROOT / TASK_PATH
    results = {}
    for case in sorted((task / 'tests/fixtures/cases').iterdir()):
        if not case.is_dir():
            continue
        results[case.name] = {
            name: runner.run_verifier(path, case)
            for name, path in [('baseline', baseline), ('revised', task)]
        }
        print(f"{case.name}: baseline={results[case.name]['baseline']['reward']} "
              f"revised={results[case.name]['revised']['reward']}", flush=True)
    output = Path(__file__).resolve().parent
    (output / 'paired-controls.json').write_text(json.dumps(results, indent=2) + '\n')
    (output / 'final-paired-verifier.json').write_text(
        json.dumps(results['valid-alternate-headings'], indent=2) + '\n')


if __name__ == '__main__':
    main()
