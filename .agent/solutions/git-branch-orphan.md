# Git Orphan Branch

## Problem

After running `git checkout -b <branch-name>`, the working directory shows all files as "new" in the staging area, and `git log` returns "no commits yet" or empty output.

## Root Cause

The branch was created as an **orphan** — a branch with no parent commit. This typically happens when:

1. The `.git` directory is in a corrupted or incomplete state (e.g., sandbox restrictions prevented refs from being written)
2. `git checkout -b` was run in a directory where HEAD points to a non-existent ref
3. A previous `git init` created a new repo but no initial commit was made before branching

## Solution

### Prevention

Always verify branch history after creation:

```bash
git checkout main
git pull
git checkout -b <branch-name>
git log --oneline -3  # MUST show existing commits
```

### Recovery

If you've already created an orphan branch:

```bash
# 1. Switch back to main
git checkout main

# 2. Delete the orphan branch
git branch -D <branch-name>

# 3. Verify main has history
git log --oneline -3

# 4. Recreate branch from main
git checkout -b <branch-name>
git log --oneline -3  # Verify again
```

If `.git` is corrupted (no history on any branch):

```bash
# 1. Re-clone the repo to a temporary directory
git clone <remote-url> ../PGC-restore

# 2. Copy .git from the restored repo
Copy-Item -Recurse -Force ../PGC-restore/.git ./.git

# 3. Verify
git log --oneline -3
```

## Verification

```bash
git log --oneline -3
# Expected: shows at least 3 commits with valid hashes
# NOT: "fatal: your current branch does not have any commits yet"
```
