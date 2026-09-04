#!/usr/bin/env bash
# Run one task through Harbor in one lane and one condition.
#
#   evals/scripts/run.sh <lane> <with-skills|baseline> [task-dir] [-- extra harbor args]
#
# Lanes:
#   nop          agent does nothing; proves the verifier scores an empty workspace 0
#   oracle       runs solution/solve.sh; proves the reference memo scores 1
#   claude-code  Claude Code CLI (Harbor built-in)
#   codex        Codex CLI (Harbor built-in)
#
# Credentials (never printed):
#   claude-code  ANTHROPIC_API_KEY, or CLAUDE_CODE_OAUTH_TOKEN (from `claude setup-token`).
#                If neither is set, the short-lived access token in
#                ~/.claude/.credentials.json is used with CLAUDE_FORCE_OAUTH=1.
#   codex        OPENAI_API_KEY, or CODEX_FORCE_AUTH_JSON=1 to use ~/.codex/auth.json.
#
# Models: override with CLAUDE_MODEL / CODEX_MODEL. Attempts per cell: ATTEMPTS (default 1).
set -euo pipefail

lane="${1:?lane}"
cond="${2:?with-skills|baseline}"
task="${3:-evals/tasks/pay-app-review/harborview-app3}"
shift 3 2>/dev/null || shift $#
if [ "${1:-}" = "--" ]; then shift; fi

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"

CLAUDE_MODEL="${CLAUDE_MODEL:-anthropic/claude-sonnet-5}"
CODEX_MODEL="${CODEX_MODEL:-openai/gpt-5.6-sol}"
ATTEMPTS="${ATTEMPTS:-1}"

stamp="$(date +%Y%m%d-%H%M%S)"
job="$(basename "$(dirname "$task")")-$(basename "$task")__${lane}__${cond}__${stamp}"

args=(run -p "$task" -o evals/jobs --job-name "$job" -k "$ATTEMPTS" -n 4 -y --artifact /app/output)

case "$cond" in
  with-skills) args+=(--skills ./skills) ;;
  baseline) ;;
  *) echo "condition must be with-skills or baseline" >&2; exit 2 ;;
esac

case "$lane" in
  nop|oracle)
    args+=(-a "$lane")
    ;;
  claude-code)
    args+=(-a claude-code -m "$CLAUDE_MODEL")
    if [ -z "${ANTHROPIC_API_KEY:-}" ] && [ -z "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]; then
      creds="$HOME/.claude/.credentials.json"
      [ -f "$creds" ] || { echo "no ANTHROPIC_API_KEY, CLAUDE_CODE_OAUTH_TOKEN, or $creds" >&2; exit 2; }
      CLAUDE_CODE_OAUTH_TOKEN="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["claudeAiOauth"]["accessToken"])' "$creds")"
      export CLAUDE_CODE_OAUTH_TOKEN
      export CLAUDE_FORCE_OAUTH=1
      echo "claude-code: using the claude.ai session token from $creds (short-lived; run 'claude setup-token' for CI)" >&2
    elif [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ] && [ -z "${ANTHROPIC_API_KEY:-}" ]; then
      export CLAUDE_FORCE_OAUTH=1
    fi
    ;;
  codex)
    args+=(-a codex -m "$CODEX_MODEL")
    if [ -z "${OPENAI_API_KEY:-}" ]; then
      [ -f "$HOME/.codex/auth.json" ] || { echo "no OPENAI_API_KEY or ~/.codex/auth.json" >&2; exit 2; }
      export CODEX_FORCE_AUTH_JSON=1
      echo "codex: using ~/.codex/auth.json (ChatGPT auth)" >&2
    fi
    ;;
  *) echo "unknown lane: $lane" >&2; exit 2 ;;
esac

echo "harbor ${args[*]} $*" >&2
exec harbor "${args[@]}" "$@"
