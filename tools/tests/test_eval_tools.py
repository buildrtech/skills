"""Local process-boundary checks; these do not claim Harbor/model integration."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('rescore', ROOT / 'evals/scripts/rescore.py')
rescore = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rescore)


class EvalToolsTest(unittest.TestCase):
    def run_wrapper(self, arguments, variables=None):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            recorder = path / 'harbor'
            recorder.write_text('#!/usr/bin/env python3\nimport json,os,sys\nprint(json.dumps({"args":sys.argv[1:],"codex_force":os.getenv("CODEX_FORCE_AUTH_JSON"),"claude_force":os.getenv("CLAUDE_FORCE_OAUTH")}))\n')
            recorder.chmod(0o755)
            env = {**os.environ, 'PATH': f'{tmp}:{os.environ["PATH"]}', **(variables or {})}
            result = subprocess.run(['bash', str(ROOT / 'evals/scripts/run.sh'), *arguments], env=env, capture_output=True, text=True, check=True)
            return json.loads(result.stdout), result.stderr

    def test_default_task_separator_and_private_arguments(self):
        result, diagnostics = self.run_wrapper(['nop', 'with-skills', '--', '--one-off-secret', 'NAME=synthetic-secret'])
        args = result['args']
        self.assertEqual(args[args.index('-p') + 1], 'evals/tasks/pay-app-review/harborview-app3')
        self.assertEqual(args[-2:], ['--one-off-secret', 'NAME=synthetic-secret'])
        self.assertNotIn('synthetic-secret', diagnostics)
        self.assertEqual(args[args.index('-n') + 1], '1')

    def test_default_without_separator_and_explicit_without_extras(self):
        default, _ = self.run_wrapper(['nop', 'baseline'])
        explicit, _ = self.run_wrapper(['oracle', 'baseline', 'evals/tasks/example'])
        self.assertEqual(default['args'][2], 'evals/tasks/pay-app-review/harborview-app3')
        self.assertEqual(explicit['args'][2], 'evals/tasks/example')

    def test_explicit_task_and_api_key_precedence(self):
        for lane, key, force, field in [('codex', 'OPENAI_API_KEY', 'CODEX_FORCE_AUTH_JSON', 'codex_force'), ('claude-code', 'ANTHROPIC_API_KEY', 'CLAUDE_FORCE_OAUTH', 'claude_force')]:
            result, _ = self.run_wrapper([lane, 'baseline', 'evals/tasks/example', '--', '--quiet'], {key: 'synthetic-key', force: '1'})
            self.assertIsNone(result[field])
            self.assertEqual(result['args'][2], 'evals/tasks/example')
            self.assertEqual(result['args'][-1], '--quiet')

    def test_reject_directory_file_and_dangling_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for target in ['/', '/etc/hosts', str(root / 'missing')]:
                link = root / 'escape'
                link.symlink_to(target)
                with self.assertRaises(ValueError):
                    rescore.reject_links(root)
                link.unlink()
            (root / 'valid.json').write_text('{}')
            rescore.reject_links(root)

    def test_rescore_rejects_link_before_verifier_or_result_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            trial = Path(tmp) / 'trial'
            task = Path(tmp) / 'task'
            (task / 'tests').mkdir(parents=True)
            (task / 'environment').mkdir()
            artifacts = trial / 'artifacts/app/output'
            artifacts.mkdir(parents=True)
            (artifacts / 'root').symlink_to('/')
            original = json.dumps({'config': {'task': {'path': str(task)}}})
            (trial / 'result.json').write_text(original)
            with self.assertRaises(ValueError):
                rescore.rescore(trial)
            self.assertEqual((trial / 'result.json').read_text(), original)
            self.assertFalse((trial / 'verifier').exists())

    def test_failed_serialization_preserves_record_and_cleans_temporary(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'result.json'
            path.write_text('{"original": true}')
            with self.assertRaises(TypeError):
                rescore.atomic_json(path, {'invalid': object()})
            self.assertEqual(json.loads(path.read_text()), {'original': True})
            self.assertEqual(list(path.parent.iterdir()), [path])
            rescore.atomic_json(path, {'reward': 1})
            self.assertEqual(json.loads(path.read_text()), {'reward': 1})


if __name__ == '__main__':
    unittest.main()
