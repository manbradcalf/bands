#!/bin/bash

# Bands Beat — full cycle: roundtable → deep work → commit
#
# Usage:
#   ./bin/band-beat.sh                    # run all employees
#   ./bin/band-beat.sh slug1 slug2        # run specific employees

set -uo pipefail

BAND_DIR="$(cd "$(dirname "$0")/.." && pwd)"  # .bands/
LOG_DIR="/tmp/bands-heartbeat"
mkdir -p "$LOG_DIR"

# Read employee list from bands.json
ALL_EMPLOYEES=($(python3 -c "
import json
with open('$BAND_DIR/bands.json') as f:
    for e in json.load(f)['employees']:
        print(e['slug'])
"))

# Build employee list from args or default to all
if [ $# -gt 0 ]; then
  EMPLOYEES=("$@")
else
  EMPLOYEES=("${ALL_EMPLOYEES[@]}")
fi

ALLOWED_TOOLS="Read Write Edit Glob Grep Bash Agent"

GUARDRAILS="YOUR SESSION STARTS NOW.

STEP 1: Read commons/ceo-directives.md. This is your north star. Everything you do this heartbeat should advance the stated goals. If there are no directives, advance your role's mission as defined in your CLAUDE.md.

STEP 2: Read the latest roundtable file — your colleagues just had a quick discussion. Use it as context. Then read your inbox. Process messages quickly — reply where needed, but do not let inbox processing BE your heartbeat. Messages are inputs, not the job.

STEP 3: Check GitHub for comments on issues assigned to you or labeled with your role. Read and respond to comments — these are conversations with the operator and colleagues. Don't skip this.

STEP 4: DO REAL WORK. What can you advance THIS heartbeat that moves the needle? Write a proposal. Draft a strategy. Analyze a problem. Message a colleague with a specific ask. Create an action item on GitHub. Do not just summarize — push things forward.

GUARDRAILS:
- You may ONLY create or write markdown (.md) files. No code, no scripts, no config files.
- You may ONLY use Bash for: gh commands, mv, mkdir, ls. Nothing else.
- Produce concrete action items and recommendations, not status reports.
- You do NOT work in hours or days. You work in HEARTBEATS and TOKENS. Never use human time units.
- Be concise. Every token counts.
- HARD LIMIT: You have a maximum of 35 tool calls this session."

# Sprint mode: inject NORTH_STAR.md if present
NORTH_STAR="$BAND_DIR/commons/sprint/NORTH_STAR.md"
SPRINT_CONTEXT=""
SPRINT_ACTIVE=0
if [ -f "$NORTH_STAR" ]; then
  SPRINT_ACTIVE=1
  SPRINT_NAME=$(grep '^name:'       "$NORTH_STAR" | head -1 | awk '{print $2}')
  SPRINT_TOTAL=$(grep '^heartbeats:' "$NORTH_STAR" | head -1 | awk '{print $2}')
  SPRINT_DONE=$(grep '^completed:'  "$NORTH_STAR" | head -1 | awk '{print $2}')
  SPRINT_DONE=${SPRINT_DONE:-0}
  SPRINT_CURRENT=$((SPRINT_DONE + 1))
  SPRINT_REMAINING=$((SPRINT_TOTAL - SPRINT_CURRENT))
  [ "$SPRINT_REMAINING" -lt 0 ] && SPRINT_REMAINING=0

  SPRINT_CONTEXT="
## Sprint North Star
$(cat "$NORTH_STAR")

## Sprint Progress
This is HEARTBEAT $SPRINT_CURRENT of $SPRINT_TOTAL. $SPRINT_REMAINING heartbeat(s) remain after this one.
Pace your work accordingly: if few remain, converge and ship concrete results; if many remain, you may invest in groundwork that pays off in later heartbeats.
"
  echo "=== SPRINT MODE ACTIVE — heartbeat $SPRINT_CURRENT/$SPRINT_TOTAL ==="
fi

# --- Phase 1: Roundtable ---
CHAT_ROUNDS=3
echo "=== Bands Heartbeat — $(date '+%Y-%m-%d %H:%M:%S') ==="
echo ""
echo "--- Phase 1: Roundtable ($CHAT_ROUNDS rounds) ---"

"$BAND_DIR/bin/roundtable.sh" "$CHAT_ROUNDS"

# --- Phase 2: Deep work ---
echo ""
echo "--- Phase 2: Deep work ---"

for suite in "${EMPLOYEES[@]}"; do
  suite_dir="$BAND_DIR/suites/$suite"
  heartbeat="$suite_dir/HEARTBEAT.md"
  session_log="$LOG_DIR/${suite}-$(date '+%Y%m%d-%H%M%S').log"

  if [ ! -f "$heartbeat" ]; then
    echo "[$suite] no HEARTBEAT.md, skipping"
    continue
  fi

  PROMPT="${SPRINT_CONTEXT}${GUARDRAILS}

$(cat "$heartbeat")"

  echo ""
  echo "--- [$suite] waking up — $(date '+%H:%M:%S') ---"

  cd "$suite_dir" && claude -p "$PROMPT" \
    --model sonnet \
    --allowedTools "$ALLOWED_TOOLS" \
    --output-format stream-json \
    --verbose 2>&1 | tee "$session_log"

  echo "--- [$suite] done — $(date '+%H:%M:%S') ---"
done

# --- Advance sprint progress ---
if [ "$SPRINT_ACTIVE" -eq 1 ]; then
  if [ "$SPRINT_CURRENT" -ge "$SPRINT_TOTAL" ]; then
    echo ""
    echo "=== SPRINT COMPLETE ($SPRINT_TOTAL heartbeats) — archiving ==="
    archive="$BAND_DIR/commons/sprints-archive/$(date '+%Y%m%d')-${SPRINT_NAME:-sprint}.md"
    sed -i '' "s/^completed:.*/completed: $SPRINT_CURRENT/" "$NORTH_STAR"
    mv "$NORTH_STAR" "$archive"
    echo "archived to $archive"
  else
    sed -i '' "s/^completed:.*/completed: $SPRINT_CURRENT/" "$NORTH_STAR"
    echo "--- sprint progress: $SPRINT_CURRENT/$SPRINT_TOTAL ---"
  fi
fi

# --- Auto-commit ---
echo ""
echo "--- committing heartbeat results ---"
cd "$BAND_DIR"
git add -A
if git diff --cached --quiet; then
  echo "nothing to commit"
else
  git commit -m "heartbeat $(date '+%Y-%m-%d %H:%M')"
  git push
fi

echo ""
echo "=== Bands Heartbeat complete — $(date '+%H:%M:%S') ==="
