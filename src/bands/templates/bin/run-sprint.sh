#!/bin/bash

# Run Sprint — loop band-beat.sh until the sprint's heartbeat count is reached.
#
# The total comes from commons/sprint/NORTH_STAR.md (heartbeats: N) and progress
# is tracked there (completed: K). band-beat.sh archives the north star on the
# final beat, so this loop stops automatically when the sprint is done.
#
# Usage:
#   ./bin/run-sprint.sh                 # run remaining beats for the active sprint
#   ./bin/run-sprint.sh 5               # run at most 5 more beats (override)
#   ./bin/run-sprint.sh 5 nadia-cto     # 5 beats, only these employees
#   ./bin/run-sprint.sh "" nadia-cto    # remaining beats, only these employees

set -uo pipefail

BAND_DIR="$(cd "$(dirname "$0")/.." && pwd)"  # .bands/
NORTH_STAR="$BAND_DIR/commons/sprint/NORTH_STAR.md"

MAX_OVERRIDE="${1:-}"
shift 2>/dev/null || true
EMPLOYEES=("$@")

if [ ! -f "$NORTH_STAR" ]; then
  echo "No active sprint (commons/sprint/NORTH_STAR.md not found)."
  echo "Scaffold one with a sprint, or create the north star first."
  exit 1
fi

i=0
while [ -f "$NORTH_STAR" ]; do
  total=$(grep '^heartbeats:' "$NORTH_STAR" | head -1 | awk '{print $2}')
  done=$(grep '^completed:'  "$NORTH_STAR" | head -1 | awk '{print $2}')
  done=${done:-0}
  remaining=$((total - done))

  if [ "$remaining" -le 0 ]; then
    echo "Sprint already complete ($done/$total)."
    break
  fi
  if [ -n "$MAX_OVERRIDE" ] && [ "$i" -ge "$MAX_OVERRIDE" ]; then
    echo "Reached override limit of $MAX_OVERRIDE beats; $remaining still remain in the sprint."
    break
  fi

  i=$((i + 1))
  echo ""
  echo "########## SPRINT BEAT $((done + 1))/$total ##########"
  "$BAND_DIR/bin/band-beat.sh" ${EMPLOYEES[@]+"${EMPLOYEES[@]}"}
done

echo ""
echo "=== run-sprint complete: ran $i heartbeat(s) ==="
