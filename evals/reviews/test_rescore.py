"""Rescore saved artifacts with the real pinned rewardkit, without model calls.

Run: python3 evals/reviews/test_rescore.py (requires uvx).
"""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("rescore", ROOT / "evals/scripts/rescore.py")
rescore = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rescore)
TASK = ROOT / "evals/tasks/rfi-drafter/sable-creek-rfi-023"


class RescoreIntegrationTest(unittest.TestCase):
    def test_null_verifier_result_recovers_with_real_reference_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            trial = Path(tmp)
            output = trial / "artifacts/app/output"
            output.mkdir(parents=True)
            shutil.copy2(TASK / "solution/reference-rfi-023.md", output / "rfi-023.md")
            exception = {"exception_type": "RewardFileNotFoundError"}
            record = {
                "config": {"task": {"path": str(TASK)}},
                "verifier_result": None,
                "exception_info": exception,
                "agent_result": {"preserved": True},
            }
            result = trial / "result.json"
            result.write_text(json.dumps(record))

            rewards = rescore.rescore(trial)

            self.assertIsNotNone(rewards)
            self.assertEqual(rewards["reward"], 1)
            saved = json.loads(result.read_text())
            self.assertEqual(saved["verifier_result"]["rewards"], rewards)
            self.assertEqual(saved["agent_result"], record["agent_result"])
            self.assertEqual(saved["superseded_exception_info"], exception)
            self.assertIsNone(saved["exception_info"])
            self.assertIn("rescored_at", saved)
            self.assertEqual(json.loads((trial / "verifier/reward.json").read_text()), rewards)
            self.assertTrue((trial / "verifier/reward-details.json").is_file())
            self.assertEqual(list(trial.glob(".result.json.*")), [])


if __name__ == "__main__":
    unittest.main()
