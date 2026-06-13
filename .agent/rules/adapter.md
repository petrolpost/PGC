# Adapter Development Standards

All adapters must follow these rules to ensure consistent version compatibility and rendering behavior.

## Architecture

- Inherit `BaseAdapter` and implement all abstract methods: `render()`, `get_target_runtime()`, `get_target_runtime_version()`, `get_supported_extensions()`
- Adapter code lives under `pgc_adapter/<runtime>/generator.py` with a corresponding `__init__.py`
- Register new adapters in `pgc_adapter/__init__.py`

## Version Compatibility

- Every adapter MUST implement `get_target_runtime_version()` returning `"runtime@X.Y"` format (e.g. `"trae@1.3"`, `"claude-code@1.0"`)
- The version number reflects the **minimum** target runtime version the adapter supports
- `check_runtime_compatibility()` from `pgc_core.validator` is used by `pgc validate` to verify document-adapter version alignment
- When a runtime introduces breaking changes, bump the adapter version and update render logic accordingly
- Old adapter versions remain compatible via SemVer comparison

## Version Upgrade Checklist

When adding a new adapter or updating for a new runtime version:

1. Update `get_target_runtime_version()` to reflect the new minimum supported version
2. Update render logic to support new features/fields introduced in that version
3. Add version compatibility test cases (compatible / version too high / runtime name mismatch / no metadata / empty metadata)
4. Update the corresponding runtime mapping doc under `docs/runtime-mapping/`

## Rendering Rules

- `render()` returns `Dict[str, str]` — keys are relative file paths, values are file contents
- Never perform IO (file writes) inside adapters
- Skip empty sections — do not generate files for empty boundaries/capabilities
- Use `in` assertions in tests, not exact string matching, to avoid fragile tests

## File Naming Convention

- Claude Code: single `CLAUDE.md`
- Trae: multiple files under `.trae/rules/` with YAML frontmatter
- Future adapters: follow the target runtime's native convention

## Runtime Mapping Documentation

Runtime mapping docs live under `docs/runtime-mapping/` and describe how PGC concepts translate to each target runtime.

### File Naming

| Pattern | When to Use | Example |
|---------|-------------|---------|
| `<runtime>.md` | Default — covers all compatible versions with same mapping strategy | `claude-code.md`, `trae.md` |
| `<runtime>@<major>.x.md` | Breaking change — when a major version requires a different mapping strategy | `claude-code@2.x.md` |

Rules:

1. **Default file** (`<runtime>.md`) always exists. Its frontmatter `versions` field specifies the compatible range (e.g. `">=1.0"`).
2. **Versioned file** (`<runtime>@<major>.x.md`) is created ONLY when a major version introduces breaking changes that require a different mapping strategy.
3. Multiple versions sharing the same mapping strategy use one file with a broad `versions` range.
4. The adapter's `get_target_runtime_version()` return value determines which mapping doc applies.

### Frontmatter Schema

Every mapping doc MUST include YAML frontmatter:

```yaml
---
runtime: <runtime-name>        # e.g. "trae", "claude-code"
versions: "<semver-range>"     # e.g. ">=1.0", ">=1.3 <2.0"
status: active | deprecated | draft
adapter: pgc_adapter.<runtime>.<AdapterClass>
---
```

### When to Create a Versioned File

1. Runtime v2.0 changes the config file format (e.g. `.trae/rules/` → `.trae/policies/`)
2. Runtime v2.0 removes or renames features that PGC maps to
3. The adapter's render logic diverges significantly between major versions

Do NOT create a versioned file for:
- Minor additions (new optional fields) — update the default doc's `versions` range
- Bug fixes or clarifications — update the default doc in place
