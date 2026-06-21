# Journal Module

Task Execution Ledger -- a standard, mountable project-operational module for recording interrupted work.

## Position in the Architecture

```text
PGC
  authority and responsibility

TGS
  traceability and verification

Journal
  startup context, events, errors, current state, handoff snapshot
```

## Core Concepts

| Concept | Meaning |
|---|---|
| Task | The unit of work being executed or resumed. |
| Event | An append-only record of something that happened during execution. |
| State | The latest durable snapshot of the task. |
| Error | A captured failure, warning, or partial failure record. |
| Handoff | A derived summary for the next agent or thread. |

## Ledger Layout

```text
.journal/
  manifest.yaml
  events.jsonl
  state.yaml
  handoff.md
  logs/
```

- `manifest.yaml` declares task identity and ledger policy.
- `events.jsonl` stores raw execution events as the source of truth.
- `state.yaml` stores the current durable snapshot.
- `handoff.md` is derived from the ledger and optimized for the next agent.
- `logs/` stores raw startup information, error output, and verification output.

## Adapter

- **journal:file** -- Renders the standard ledger layout as files in `.journal/`.

## Configuration

Mount through governance configuration:

```yaml
modules:
  journal:
    enabled: true
    contract: .journal/manifest.yaml
    adapter: journal:file
    record_format: jsonl
    startup_capture: true
```

## Validation Rules

1. A mounted journal module must have a valid namespaced adapter ID.
2. The journal must preserve append-first event history.
3. The handoff view must be derived from ledger records, not manually treated as the source of truth.
4. The journal must not require PGC or TGS internals to function.

## Non-Goals

The journal does not:

- enforce execution order;
- schedule tasks;
- replace traceability evidence;
- define governance boundaries.
