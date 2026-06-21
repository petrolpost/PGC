# Issue-Driven Development

This rule defines the complete lifecycle for Issue-driven development in the PGC project.

## Phase 1: Issue Identification & Submission

### When to Create an Issue

- **Feature**: New capability, adapter, or enhancement
- **Bug**: Unexpected behavior or regression
- **Refactor**: Structural improvement without behavior change
- **Docs**: Documentation update or addition

### Issue Template

```markdown
## Context
<Why this issue exists, what problem it solves>

## Tasks
- [ ] <Specific, verifiable task>
- [ ] <Specific, verifiable task>

## DoD (Definition of Done)
<Must be verifiable: test commands, file existence, output format>
```

### DoD Requirements

- Must include at least one **verifiable** criterion
- Verifiable means: a command can be run, a file can be checked, or an output format can be validated
- Avoid vague criteria like "works correctly" — specify the test or check

## Phase 2: Claim & Branch Creation

### Claim the Issue

```bash
$env:GH_TOKEN="<token>"
gh issue edit <N> --add-assignee "@me"
```

### Branch Naming Convention

```
<type>/<issue-number>-<short-description>

Types: feat / fix / refactor / docs
Examples:
  feat/13-trae-adapter
  fix/42-validation-error
  refactor/16-agent-rule-system
```

### Branch Creation Flow (CRITICAL)

```bash
# 1. Switch to main and pull latest
git checkout main
git pull

# 2. Create branch from main
git checkout -b <branch-name>

# 3. VERIFY: must have commit history
git log --oneline -3
```

**Verification checkpoint**: `git log` MUST show existing commits. If you see "no commits yet" or empty output, the branch is **orphaned** — delete it and retry.

### Common Pitfall: Orphan Branch

**Symptom**: After `git checkout -b`, all files appear as "new" in staging area.

**Root cause**: Branch was created without a parent commit (no history).

**Prevention**: Always verify `git log` after branch creation. See `.agent/solutions/git-branch-orphan.md` for details.

## Phase 3: Development Process

### Spec First

Every Issue MUST have a spec and test plan before implementation:

- Spec: `docs/issues/<issue-number>-<slug>/spec.md`
- Test plan: `docs/issues/<issue-number>-<slug>/test-plan.md`

Spec must include:
1. **Requirements analysis** — background, goals, constraints
2. **Design** — architecture, data flow, interfaces
3. **Execution plan** — step-by-step tasks with deliverables

Test plan must include:
- Verifiable test cases with commands and expected output
- DoD checklist

### Traceability Handoff

If the repository or delivery flow enables TGS, use `tgs/operating-spec.md` to record Anchor, Action, Artifact, and Verification.

This file governs lifecycle delivery. It does not define TGS Core, the GitHub-backed TGS profile boundary, the TGS command surface, or integrity-level policy.

### Commit Convention

```
<type>(<scope>): <description> (#<issue-number>)

Types: feat / fix / refactor / docs / test / chore
Examples:
  feat(adapter): add TraeAdapter for .trae/rules/ generation (#13)
  fix(validator): handle empty metadata in compatibility check (#42)
```

### Staging Area Check

Before committing, verify only relevant files are staged:

```bash
git status
# Confirm only files related to the current issue are staged
# If unrelated files appear, use git restore --staged <file> to unstage
```

## Phase 4: PR Submission & Merge

### PR Description Template

```markdown
## Summary
<One-line description>

## Changes
- <Change 1>
- <Change 2>

## Test Results
<Command output or test summary>

Closes #<N>
```

### PR Checklist

- [ ] PR description includes `Closes #<N>`
- [ ] All test plan items pass
- [ ] No unrelated files in the diff
- [ ] Branch is based on latest `main`

### After Merge

```bash
# Switch back to main
git checkout main
git pull

# Delete local branch
git branch -d <branch-name>

# Delete remote branch (if pushed)
git push origin --delete <branch-name>
```
