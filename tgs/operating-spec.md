# TGS Operating Spec

This file defines how TGS is operated inside the PGC repository.

It defines how this repository adopts the GitHub Issue-driven profile, not the full definition of TGS Core and not a future package installation format.

It closes the gap between:

- `Agent.md`, which routes an agent to the right rule set
- `.agent/rules/issue-driven.md`, which governs delivery lifecycle
- `tgs/README.md`, which defines concepts and integrity levels
- `tgs/profiles/github-issue-driven.md`, which defines the GitHub-backed profile mapping
- `tgs/instructions.md`, which defines the rendered instruction surface

## Current State vs Target State

| Source | Current State | Gap | Target State |
|---|---|---|---|
| `Agent.md` | Defines project-wide entry rules and on-demand navigation. | TGS has no explicit navigation entry. | Keep `Agent.md` as entry only and add TGS navigation. |
| `.agent/rules/issue-driven.md` | Defines Issue lifecycle, branch rules, spec-first, PR closing. | It governs delivery, but not traceability semantics. | Keep lifecycle governance here and hand off traceability operation to TGS. |
| `tgs/README.md` | Defines TGS concepts and integrity levels. | It explains what TGS is, but not how this repo should operate it. | Keep it as concept overview and document map. |
| `tgs/profiles/github-issue-driven.md` | Defines the GitHub-backed TGS mapping. | The mapping is not yet isolated as a profile artifact. | Keep platform mapping in the profile and reference it from repo rules. |
| `tgs/instructions.md` | Defines slash command surface and discipline. | It can be mistaken for the full operating rule set. | Keep it as rendered instruction contract only. |
| `tgs/*` | Includes contract, injection, adapter, and audit docs. | No single file defines repository operating policy. | Add `tgs/operating-spec.md` as the operating authority. |

## Document Responsibilities

| File | Responsibility | Should Not Contain |
|---|---|---|
| `Agent.md` | Project entry, always-on rules, on-demand navigation. | Detailed TGS procedures or trace record templates. |
| `.agent/rules/issue-driven.md` | Work intake, branch/spec/commit/PR lifecycle. | TGS command catalog or integrity-level policy. |
| `tgs/README.md` | TGS positioning, concepts, integrity levels, doc map. | Repository-specific step-by-step operating workflow. |
| `tgs/profiles/github-issue-driven.md` | GitHub object mapping and profile-level semantics. | Repository ownership, renderer behavior, or package install flow. |
| `tgs/instructions.md` | Rendered command surface and minimal discipline. | Full repo workflow, ownership rules, or migration policy. |
| `tgs/operating-spec.md` | Repository operating workflow, phase mapping, integrity-level usage, retirement plan. | Low-level schema fields already defined in `traceability-contract.yaml`. |

## Layer Boundary In This Repo

| Layer | Repository Meaning | Current Home |
|---|---|---|
| `TGS Core` | Traceability concepts, integrity levels, and contracts that remain platform-agnostic. | `tgs/README.md`, `tgs/traceability-contract.yaml`, `tgs/audit/` |
| `TGS Profile` | The GitHub-backed operating interpretation used by this repository. | `tgs/operating-spec.md` |
| `TGS Adapter` | Rendering behavior that produces runtime-facing `.tgs/*` outputs. | `tgs/instructions.md`, `tgs/adapters/`, `governance_config/assembler.py` |
| `TGS Package` | A future installable distribution unit for TGS. | Not defined in this issue or file. |

The repository rule for this issue is:

- treat GitHub-backed TGS as a profile layered on top of TGS Core
- keep adapter behavior separate from profile meaning
- do not treat `.tgs/` as a package format
- leave formal package design to follow-up work

## Repository Operating Rules

## Repository Profile Adoption

This repository adopts `tgs/profiles/github-issue-driven.md` as its canonical GitHub-backed TGS profile.

The split of responsibility is:

- the profile defines GitHub object mapping and profile-level semantics
- this operating spec defines repository-local adoption, integrity defaults, and handoff rules
- `.agent/rules/issue-driven.md` defines delivery mechanics
- `tgs/instructions.md` defines only the rendered command surface

When repository workflow interpretation changes, update the profile first if the change affects GitHub object mapping, then update this file for repository-local adoption rules.

### 1. Scope

Use TGS when the work needs an auditable chain from intent to evidence, especially for:

- issue-bound delivery
- approval-gated changes
- generated governance artifacts
- reviewable documentation or code changes

### 2. Anchor Policy

Every traceability chain starts from one explicit anchor. Preferred anchor order:

1. GitHub Issue
2. Approval record
3. Task record
4. Decision record

No anchor, no TGS action record.

### 3. Phase Mapping

Map TGS onto Issue-Driven Development as follows:

| Issue-Driven Phase | TGS Expectation |
|---|---|
| Phase 1: Issue Identification & Submission | Establish the Anchor and expected Artifacts. |
| Phase 2: Claim & Branch Creation | Record the Action that claims or starts the work when traceability is required. |
| Phase 3: Development Process | Keep Action -> Artifact links for meaningful outputs such as spec, tests, code, docs, or generated rule files. |
| Phase 4: PR Submission & Merge | Attach Verification evidence before closing the chain. |

### 3.1 Profile Reference

Use `tgs/profiles/github-issue-driven.md` for the canonical GitHub object mapping.

The minimum repository-local interpretation remains:

- Anchor: GitHub Issue
- Action: claim, commit, PR update, merge-adjacent workflow transitions, and close
- Artifact: Issue text, spec, test plan, commit history, PR body/diff, and review records
- Verification: PR linkage, status checks, test outputs, review conclusions, merge evidence, and final close state

This repository adopts that mapping as the first repository-local GitHub-backed TGS profile. It is a practical profile layered on top of TGS Core, not the full limit of what TGS can represent.

### 4. Artifact Policy

Artifacts should be concrete and reviewable. Typical artifacts include:

- `docs/issues/<issue>/spec.md`
- `docs/issues/<issue>/test-plan.md`
- changed source files
- generated governance files under `.tgs/` or runtime-specific outputs
- PR descriptions, audit reports, or review summaries

### 5. Verification Policy

Verification must be explicit and reproducible. Accepted examples:

- test commands and outputs
- file existence checks
- schema validation results
- review decisions with traceable conclusions

No verification, no close.

## Integrity Level Guidance

| Scenario | Recommended Level | Reason |
|---|---|---|
| Lightweight docs update with one anchor and one artifact | L1 | Basic provenance is enough. |
| Standard feature, bug fix, refactor, or rules change | L2 | Needs Anchor, Action, Artifact, and Verification. |
| Compliance-sensitive, release-critical, or multi-step generated output | L3 | Needs ordering and consistency checks. |

Unless a stricter requirement exists, this repository should treat rule changes and code changes as **L2 by default**.

## Operating File Layout

| Location | Role |
|---|---|
| `tgs/` | Source-of-truth specifications, templates, adapters, and operating rules. |
| `.tgs/` | Rendered, workspace-local operating outputs such as instructions and audit reports. |
| `tgs/injection/*.yaml` | Example composition entry points for standalone TGS or combined PGC + TGS usage. |

This is why the operating spec belongs in `tgs/operating-spec.md`: it is part of the TGS source package, not a generated workspace artifact.

It also means `.tgs/` should be read as rendered runtime output, not as the final definition of an installable TGS package.

## Old Rule Retirement Plan

### Stage 1: Introduce Clear Ownership

- Add `tgs/operating-spec.md` as the only repository-level TGS operating authority.
- Update `Agent.md` so TGS workflow navigation points to `tgs/operating-spec.md` as the TGS entry, while keeping `.agent/rules/issue-driven.md` as the lifecycle companion.
- Add a handoff note from `.agent/rules/issue-driven.md` to TGS.

### Stage 2: Shrink Legacy Overlap

- Keep `.agent/rules/issue-driven.md` as a lifecycle rule and compatibility handoff, not the TGS operating authority.
- Keep `tgs/README.md` focused on positioning, concepts, and document map.
- Keep `tgs/instructions.md` focused on command surface and minimal discipline.
- Do not add new repository workflow details to `README.md` or `instructions.md`.

### Stage 3: Enforce Through Future Changes

- Any new TGS workflow rule must be added to `tgs/operating-spec.md` first.
- If a summary is needed elsewhere, add a short pointer instead of duplicating rules.
- When renderer behavior changes, align generated `.tgs/*` outputs with the boundaries defined here.
