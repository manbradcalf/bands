# Adapter: claude (Claude Code)
# harness_run <role> <model> <prompt>
# Runs one non-interactive session in the current directory and returns claude's exit code.
# Models for reference: work "sonnet", roundtable "haiku".
# The work role also allows Agent (subagents), which band-beat.sh has always granted.

harness_run() {
  local role="$1" model="$2" prompt="$3"
  case "$role" in
    work)
      claude -p "$prompt" --model "$model" \
        --allowedTools "Read Write Edit Glob Grep Bash Agent" \
        --output-format stream-json --verbose < /dev/null
      ;;
    roundtable)
      claude -p "$prompt" --model "$model" \
        --allowedTools "Read Write" < /dev/null
      ;;
    *)
      echo "claude adapter: unknown role '$role' (expected work or roundtable)" >&2
      return 2
      ;;
  esac
}
