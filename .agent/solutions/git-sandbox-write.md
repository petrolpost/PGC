# Git Sandbox Write Restriction

## Problem

Git operations (checkout, branch creation, pull) fail silently or produce unexpected results. The `.git` directory appears to exist but refs/HEAD are not properly updated. Symptoms include:

- `git checkout -b` creates an orphan branch
- `git status` shows all files as untracked
- `git log` returns empty or "no commits yet"

## Root Cause

When running in **Trae IDE's sandbox mode**, the sandbox restricts write access to certain directories, including `.git/`. This prevents Git from updating internal files such as:

- `.git/HEAD` — current branch reference
- `.git/refs/heads/` — branch pointers
- `.git/index` — staging area

Git commands appear to succeed but the internal state is not persisted, leading to inconsistent repository state.

## Solution

### Option 1: Disable Sandbox Restrictions

Configure Trae IDE to allow write access to the project directory:

1. Open Trae IDE settings
2. Navigate to sandbox/security settings
3. Allow write access for the project workspace directory
4. Restart the IDE

### Option 2: Work Outside Sandbox

Run git operations in an external terminal (not within Trae's sandboxed terminal):

```bash
# In an external terminal (PowerShell, cmd, etc.)
cd <project-directory>
git checkout -b <branch-name>
git log --oneline -3  # Verify
```

### Option 3: Restore .git from Clone

If `.git` is already corrupted:

```bash
# Clone to temporary directory
git clone <remote-url> ../PGC-restore

# Copy .git
Copy-Item -Recurse -Force ../PGC-restore/.git ./.git

# Verify
git log --oneline -3
```

## Verification

```bash
# After creating a branch, verify the .git state is correct
git log --oneline -3
git status
# Expected: git log shows history, git status shows correct branch name
```
