# GH_TOKEN Scope Insufficient

## Problem

`gh auth login --with-token` fails with an error about missing scopes, or `gh` commands that require `read:org` scope fail with permission errors.

Error example:
```
error: read:org scope is required
```

## Root Cause

The `GH_TOKEN` (GitHub Personal Access Token) was generated without the `read:org` scope, which is required by `gh auth login` to verify organization membership. The `gh` CLI checks for this scope during authentication even when not performing org-related operations.

## Solution

### Option 1: Create Token with Required Scopes

1. Go to GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Create a new token with these scopes:
   - `repo` — full control of private repositories
   - `read:org` — read organization membership
3. Set the new token as `GH_TOKEN`

### Option 2: Use Token Directly (Skip gh auth login)

If you only need basic repo operations, set the token as an environment variable and use `gh` commands directly:

```powershell
$env:GH_TOKEN="<your-token>"
gh issue list
gh pr create --title "..." --body "..."
```

Note: Some `gh` commands may still fail if they require specific scopes.

### Option 3: Browser-Based Auth

```bash
gh auth login
# Choose: GitHub.com → HTTPS → Login with a web browser
# Follow the browser prompt to authorize
```

## Verification

```bash
$env:GH_TOKEN="<token>"
gh auth status
# Expected: shows authenticated user with token scopes listed
```
