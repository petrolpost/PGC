# Technical Solutions Index

Solutions to technical problems encountered during development. Each file follows a consistent structure: Problem → Root Cause → Solution → Verification.

## Git

- [git-branch-orphan.md](git-branch-orphan.md) — `git checkout -b` creates orphan branch with no commit history
- [git-sandbox-write.md](git-sandbox-write.md) — Trae sandbox blocks .git directory writes, causing refs update failure

## GitHub CLI

- [gh-token-scope.md](gh-token-scope.md) — GH_TOKEN missing `read:org` scope causes `gh auth login` failure

## How to Add a New Solution

1. Create `<category>-<short-name>.md` in this directory
2. Follow the template: Problem → Root Cause → Solution → Verification
3. Add an entry to the appropriate category section above
4. Commit with message: `docs(solutions): add <short-name> solution`
