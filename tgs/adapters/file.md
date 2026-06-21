# TGS File Adapter

The file adapter renders TGS traceability guidance into local project files.

## Adapter ID

```text
tgs:file
```

## Rendered Outputs

| Output | Purpose |
|---|---|
| `.tgs/instructions.md` | Agent-facing traceability instructions. |
| `.tgs/audit-report.md` | Human-readable audit report template. |

The adapter does not call external APIs. It only renders file-based instructions and templates.
