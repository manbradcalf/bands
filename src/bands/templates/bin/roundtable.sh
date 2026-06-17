#!/bin/bash

# Bands Roundtable — fast, iterative conversation
#
# Usage:
#   ./bin/roundtable.sh              # 5 rounds
#   ./bin/roundtable.sh 3            # 3 rounds
#   ./bin/roundtable.sh 5 "topic"    # 5 rounds on a topic

set -uo pipefail

BAND_DIR="$(cd "$(dirname "$0")/.." && pwd)"  # .bands/

if [[ "${1:-}" =~ ^[0-9]+$ ]]; then
  ROUNDS="$1"
  TOPIC="${2:-}"
else
  ROUNDS=5
  TOPIC="${1:-}"
fi

# Read employee list from bands.json
EMPLOYEES=($(python3 -c "
import json
with open('$BAND_DIR/bands.json') as f:
    for e in json.load(f)['employees']:
        print(e['slug'])
"))

TIMESTAMP=$(date '+%Y-%m-%d-%H%M')

# Sprint mode: write to sprint/roundtables/ if active
NORTH_STAR="$BAND_DIR/commons/sprint/NORTH_STAR.md"
if [ -f "$NORTH_STAR" ]; then
  mkdir -p "$BAND_DIR/commons/sprint/roundtables"
  ROUNDTABLE="$BAND_DIR/commons/sprint/roundtables/roundtable-${TIMESTAMP}.md"
else
  ROUNDTABLE="$BAND_DIR/commons/roundtables/roundtable-${TIMESTAMP}.md"
fi

if [ -n "$TOPIC" ]; then
  cat >"$ROUNDTABLE" <<EOF
# Roundtable — $TIMESTAMP

**Topic:** $TOPIC

---

EOF
else
  cat >"$ROUNDTABLE" <<EOF
# Roundtable — $TIMESTAMP

**Topic:** Open discussion. Check directives for context.

---

EOF
fi

PROMPT_TEMPLATE='You are in a fast roundtable discussion with your colleagues. This is NOT a deep work session — it is a quick, iterative conversation.

RULES:
- Read the roundtable file and ADD YOUR TAKE in 2-3 sentences MAX.
- React to what others said. Build on ideas. Push back. Ask questions. Riff.
- Do NOT summarize, do NOT write long paragraphs, do NOT repeat what others said.
- Write like you are talking, not writing a memo.
- Append your entry to the roundtable file in this format:

**[Your Name] ([Your Role]):** Your 2-3 sentences here.

- CRITICAL: Only write your OWN entry. NEVER write entries for the human operator or any other participant.
- If this is round 1, you may also read commons/ceo-directives.md for context.
- The roundtable file is: ROUNDTABLE_PATH
- DO NOT touch inbox/ or any files outside the roundtable file and ceo-directives.md.'

echo "=== Roundtable — $ROUNDS rounds — $(date '+%H:%M:%S') ==="

for round in $(seq 1 "$ROUNDS"); do
  echo ""
  echo "--- Round $round of $ROUNDS — $(date '+%H:%M:%S') ---"

  for suite in "${EMPLOYEES[@]}"; do
    suite_dir="$BAND_DIR/suites/$suite"
    name=$(echo "$suite" | cut -d- -f1)

    PROMPT="${PROMPT_TEMPLATE//ROUNDTABLE_PATH/$ROUNDTABLE}"

    cd "$suite_dir" && claude -p "$PROMPT" \
      --model haiku \
      --allowedTools "Read Write"

    echo "  [$name] done"
  done
done

echo ""
echo "=== Roundtable complete — $ROUNDS rounds — $(date '+%H:%M:%S') ==="
echo "Thread: $ROUNDTABLE"
