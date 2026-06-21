# TGS: Traceability Governance System

TGS defines traceability governance for Agent-assisted work. It is orthogonal to PGC.

PGC answers:

```text
Who is accountable, under what boundaries, with what declared capabilities?
```

TGS answers:

```text
Why does an action happen, who performed it, what artifact was produced, and how was it verified?
```

## Core Concepts

| Concept | Meaning |
|---|---|
| Anchor | The traceability starting point, such as an Issue, approval, task, or decision record. |
| Action | A performed operation tied to an Anchor. |
| Artifact | A produced output, such as code, docs, config, report, or generated rule file. |
| Verification | Evidence that the traceability chain is complete and acceptable. |

## Integrity Levels

| Level | Meaning |
|---|---|
| L1 | Basic traceability: Anchor and Artifact are recorded. |
| L2 | Complete traceability: Anchor, Action, Artifact, and Verification are recorded. |
| L3 | Audit traceability: L2 plus ordering and consistency checks. |
