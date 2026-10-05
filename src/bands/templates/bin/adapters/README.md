# Harness adapters

Each file here teaches the band how to run one agent harness. `bin/config.sh` sources the one named in `bands.json`:

```json
"harness": {
  "adapter": "claude",
  "models": { "work": "sonnet", "roundtable": "haiku" }
}
```

To switch harness, change `adapter` and the two model IDs. Model IDs are passed to the harness untouched. For one run only: `BANDS_ADAPTER=pi BANDS_WORK_MODEL=<model> BANDS_ROUNDTABLE_MODEL=<model> ./bin/band-beat.sh`.

Shipped adapters: `claude` (Claude Code, the default) and `pi`.

## Roles

The scripts make only two kinds of call:

| Role | Used by | Tools | Output |
|------|---------|-------|--------|
| `work` | band-beat.sh, beat.sh | read, write, edit, file search, list, bash (claude also allows Agent) | The harness's JSONL event stream, for logs |
| `roundtable` | roundtable.sh | read, write | Plain text |

## Adding a harness

1. Copy `claude.sh` or `pi.sh` to `<name>.sh`.
2. Implement `harness_run <role> <model> <prompt>` for the two roles above.
3. Rules: close stdin (`< /dev/null`), never grant a role more tools than above, print to stderr and return non-zero on an unknown role, and do nothing else (no logging, no `cd`, no retries).
4. Set `harness.adapter` to `<name>` in `bands.json`.
