# TGS Instructions

TGS can expose traceability operations through rendered instructions.

This file defines the instruction surface only. Repository operating policy lives in `tgs/operating-spec.md`.

## Slash Command Surface

```text
/tgs anchor create
/tgs action record
/tgs artifact record
/tgs verify
/tgs audit
```

## Discipline

- No context, no action.
- No verification, no close.
- No traceability, no completion.
- Preserve ordering between Anchor, Action, Artifact, and Verification.

## GitHub Issue-driven Reference

In this repository, GitHub Issue-driven delivery is the default operational expression of TGS.

| TGS Operation | GitHub-Backed Reference |
|---|---|
| Anchor | Create or reference the GitHub Issue that authorizes the work. |
| Action | Record issue claim, commit creation, PR submission, and final close actions. |
| Artifact | Link the spec, test plan, changed files, and PR summary or diff. |
| Verification | Link test evidence, review outcomes, and merge evidence before closure. |

## Boundary

- Put repository workflow rules in `tgs/operating-spec.md`.
- Keep this file minimal so generated `.tgs/instructions.md` can stay focused on agent-facing operations.
