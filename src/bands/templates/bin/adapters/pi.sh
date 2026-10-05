# Adapter: pi
# harness_run <role> <model> <prompt>
# Runs one non-interactive session in the current directory and returns pi's exit code.
# stdin is closed because pi hangs in print mode if it's left open.

harness_run() {
  local role="$1" model="$2" prompt="$3"
  case "$role" in
    work)
      pi -p "$prompt" --model "$model" \
        --tools read,write,edit,grep,find,ls,bash \
        --mode json < /dev/null
      ;;
    roundtable)
      pi -p "$prompt" --model "$model" \
        --thinking off \
        --tools read,write < /dev/null
      ;;
    *)
      echo "pi adapter: unknown role '$role' (expected work or roundtable)" >&2
      return 2
      ;;
  esac
}
