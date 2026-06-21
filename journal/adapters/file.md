# Journal File Adapter

## Adapter ID

`journal:file`

## Output

Renders the standard task execution ledger layout as files in `.journal/`:

| File | Purpose |
|---|---|
| `.journal/manifest.yaml` | Task identity and ledger policy declaration. |
| `.journal/events.jsonl` | Append-only event log (source of truth). |
| `.journal/state.yaml` | Current durable task state snapshot. |
| `.journal/handoff.md` | Derived handoff summary for the next agent. |
| `.journal/logs/README.md` | Placeholder for the logs directory. |

## Behavior

- Pure file rendering, no external API calls.
- `events.jsonl` starts empty and is appended to during execution.
- `state.yaml` is initialized with `status: pending` and `phase: init`.
- `handoff.md` is a template with placeholder sections for auto-generation.
- The adapter respects `record_format` and `startup_capture` from the module configuration.
