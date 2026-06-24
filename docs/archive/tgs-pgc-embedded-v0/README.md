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

## Document Map

| File | Role |
|---|---|
| `tgs/README.md` | Positioning, concepts, integrity levels, and navigation. |
| `tgs/operating-spec.md` | Repository operating policy for running TGS with Issue-driven delivery. |
| `tgs/instructions.md` | Rendered instruction surface for agent-facing TGS commands. |
| `tgs/traceability-contract.yaml` | Traceability contract schema and required fields. |
| `tgs/adapters/` | Adapter-specific rendering behavior. |
| `tgs/injection/` | Example composition entry points. |
| `tgs/audit/` | Audit checklist and report templates. |

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

## Layer Boundaries

| Layer | Role | Should Not Contain |
|---|---|---|
| `TGS Core` | Defines traceability concepts, integrity levels, and contracts. | GitHub-specific objects or repository workflow steps. |
| `TGS Profile` | Defines how one platform or repository expresses TGS. | Core concept ownership or package installation behavior. |
| `TGS Adapter` | Renders TGS content into runtime-facing outputs. | Repository operating policy or package format. |
| `TGS Package` | Defines a future installable distribution unit for TGS. | Workspace-local rendered outputs such as `.tgs/*`. |

This repository currently ships:

- `TGS Core` material under `tgs/README.md`, `tgs/traceability-contract.yaml`, and related audit docs
- one repository-local `TGS Profile`, implemented as a GitHub-backed operating profile
- one file-rendering `TGS Adapter`, exposed through `tgs:file`

It does not yet define a formal installable `TGS Package` format.

## Repository Profile

This repository uses GitHub Issue-driven delivery as the first concrete GitHub-backed TGS profile.

| GitHub Workflow Object | TGS Meaning |
|---|---|
| GitHub Issue | Default Anchor |
| `docs/issues/<issue>/spec.md` | Artifact |
| `docs/issues/<issue>/test-plan.md` | Artifact |
| commit / PR submission / close | Action |
| review / merge / test evidence | Verification |

Use `tgs/operating-spec.md` for the full repository mapping and lifecycle interpretation. Use `.agent/rules/issue-driven.md` for the delivery mechanics that produce those GitHub objects.

## Repository Usage Boundary

- `Agent.md` decides when TGS documents should be loaded.
- `.agent/rules/issue-driven.md` governs the delivery lifecycle.
- `tgs/operating-spec.md` governs the GitHub-backed TGS profile used in this repository.
- `tgs/instructions.md` stays minimal so rendered `.tgs/instructions.md` remains concise.
- `tgs/` is the TGS source-of-truth directory; `.tgs/` is the rendered runtime output directory.
