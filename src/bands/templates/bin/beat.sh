#!/bin/bash

# Bands Beat — wake one employee to do work
#
# Usage:
#   ./bin/beat.sh <suite-slug>

set -uo pipefail

BAND_DIR="$(cd "$(dirname "$0")/.." && pwd)"  # .bands/
LOG_DIR="/tmp/bands-heartbeat"
mkdir -p "$LOG_DIR"

SUITE="$1"
SUITE_DIR="$BAND_DIR/suites/$SUITE"

if [ ! -d "$SUITE_DIR" ]; then
  echo "suite not found: $SUITE"
  exit 1
fi

HEARTBEAT="$SUITE_DIR/HEARTBEAT.md"

if [ ! -f "$HEARTBEAT" ]; then
  echo "[$SUITE] no HEARTBEAT.md, skipping"
  exit 0
fi

PROMPT=$(cat "$HEARTBEAT")

SESSION_LOG="$LOG_DIR/${SUITE}-$(date '+%Y%m%d-%H%M%S').log"

echo "[$SUITE] waking up — $(date '+%H:%M:%S')"

cd "$SUITE_DIR" && claude -p "$PROMPT" --model sonnet --output-format stream-json --verbose 2>&1 | tee "$SESSION_LOG"

echo "[$SUITE] done — $(date '+%H:%M:%S')"
echo "$(date '+%Y-%m-%d %H:%M:%S') $SESSION_LOG" >>"$LOG_DIR/${SUITE}.log"
