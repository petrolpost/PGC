# GitHub Issue-driven Profile

This file defines the first concrete GitHub-backed TGS profile used by the PGC repository.

It captures GitHub object mapping and profile-level traceability semantics.

Use `tgs/operating-spec.md` for repository-local adoption rules, integrity defaults, and rule handoff boundaries.

## Profile Scope

This profile assumes:

- GitHub Issue is the default Anchor
- repository work is tracked through issue-bound delivery
- review, merge, and test evidence are preserved before closure
- repository-local lifecycle mechanics continue to live in `.agent/rules/issue-driven.md`

## GitHub Object Mapping

| GitHub Object or Event | TGS Role | Minimum Repository Interpretation |
|---|---|---|
| GitHub Issue title, body, labels, and DoD | Anchor + Artifact | The Issue is the default starting point for the chain, and its text is a reviewable statement of intent, scope, and completion criteria. |
| Issue claim, assignment, or linked working branch | Action | Claiming the Issue records that work has been intentionally started under the Anchor. |
| `docs/issues/<issue>/spec.md` | Artifact | The spec is the reviewable design artifact linked back to the Anchor. |
| `docs/issues/<issue>/test-plan.md` | Artifact | The test plan is the reviewable verification-planning artifact linked back to the Anchor. |
| Git commit that references the Issue | Action + Artifact | A commit records a concrete delivery step, and the commit message plus diff are traceable output under the Anchor. |
| Pull request open or update event | Action + Artifact | Opening or updating a PR is a delivery action; the PR body, linked Issue reference, and diff are reviewable artifacts. |
| Review decision or review comment | Artifact + Verification | Review records are preserved evidence of acceptance, rejection, or required follow-up; approval or change request are concrete forms of a review decision or review comment. |
| Status checks, test results, or required check conclusions on the PR | Verification | Checks provide explicit, reproducible verification evidence tied to the change set. |
| Merge commit or Merge event | Artifact + Verification | Merge records the landed result and confirms the reviewed change has entered the repository history. |
| Issue Close event or closed state linked to the merged PR | Action + Verification | Close is the terminal workflow action, and the closed state is only valid after verification evidence is attached. |

## Minimum Interpretation

- Anchor: GitHub Issue
- Action: claim, commit, PR update, merge-adjacent workflow transitions, and close
- Artifact: Issue text, spec, test plan, commit history, PR body/diff, and review records
- Verification: PR linkage, status checks, test outputs, review conclusions, merge evidence, and final close state

This profile is layered on top of TGS Core and does not define adapter behavior, package format, or repository ownership policy.
