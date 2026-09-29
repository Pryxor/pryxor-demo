#!/usr/bin/env bash
# seed_workbench.sh — reset the demo's runtime state.
#
# Wipes: mail/, transcripts/, logs/, audit/
# Keeps: agent_workspace/ (the decoy SSH key and other fixtures)
#
# A separate concern: to reset the bank, use `make clean` (deletes volumes).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "[seed] resetting mail sink..."
mkdir -p mail
find mail -maxdepth 1 -name '*.eml' -delete 2>/dev/null || true
touch mail/.gitkeep

echo "[seed] resetting transcripts/logs/audit..."
rm -rf transcripts logs audit
mkdir -p transcripts logs audit
touch transcripts/.gitkeep audit/.gitkeep

echo "[seed] done — clean runtime state ready."
echo "       (agent_workspace/ is preserved on purpose.)"
