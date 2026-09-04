#!/bin/bash
# Harbor verifier entry point. Runs after the agent finishes, inside the
# same container. Writes /logs/verifier/reward.json via rewardkit.
set -u
mkdir -p /logs/verifier

# The environment image is python:3.12; install the pinned verifier package.
if ! python3 -c "import rewardkit" 2>/dev/null; then
  pip install --quiet --disable-pip-version-check "harbor-rewardkit==0.2.0" \
    || { echo "verifier: failed to install rewardkit" >&2; exit 3; }
fi

cd /tests
python3 -m rewardkit /tests --workspace /app --output /logs/verifier/reward.json
status=$?

if [ ! -s /logs/verifier/reward.json ]; then
  echo "verifier: rewardkit wrote no reward (exit $status)" >&2
  exit 3
fi
exit 0
