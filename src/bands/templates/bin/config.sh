# Shared runtime config. Sourced by band-beat.sh, beat.sh and roundtable.sh.
# The harness and its models live in bands.json under "harness".
# If that block is missing, it defaults to Claude Code with sonnet (work) and haiku (roundtable).
# One-run overrides: BANDS_ADAPTER, BANDS_WORK_MODEL, BANDS_ROUNDTABLE_MODEL.

_BANDS_BIN="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_BANDS_JSON="$_BANDS_BIN/../bands.json"

_harness() {
  python3 -c "
import json, sys
h = json.load(open(sys.argv[1])).get('harness') or {}
models = {'work': 'sonnet', 'roundtable': 'haiku', **h.get('models', {})}
print(models[sys.argv[3]] if sys.argv[2] == 'model' else h.get('adapter', 'claude'))
" "$_BANDS_JSON" "$@"
}

ADAPTER="${BANDS_ADAPTER:-$(_harness adapter)}"
WORK_MODEL="${BANDS_WORK_MODEL:-$(_harness model work)}"
ROUNDTABLE_MODEL="${BANDS_ROUNDTABLE_MODEL:-$(_harness model roundtable)}"

if [ ! -f "$_BANDS_BIN/adapters/$ADAPTER.sh" ]; then
  echo "bands: unknown harness adapter '$ADAPTER'. Available: $(cd "$_BANDS_BIN/adapters" && ls *.sh | sed 's/\.sh$//' | tr '\n' ' ')" >&2
  exit 1
fi
source "$_BANDS_BIN/adapters/$ADAPTER.sh"

# agent_run <role> <prompt> — runs one session in the current directory
agent_run() {
  local role="$1" prompt="$2" model
  case "$role" in
    work) model="$WORK_MODEL" ;;
    roundtable) model="$ROUNDTABLE_MODEL" ;;
    *) echo "agent_run: unknown role '$role' (expected work or roundtable)" >&2; return 2 ;;
  esac
  harness_run "$role" "$model" "$prompt"
}
