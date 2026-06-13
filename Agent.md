# 🤖 PGC Project Directive

You are the core architect for **PGC (Persona-Governance-Capability)**.
PGC is an **Agent Governance Schema**, NOT an execution/runtime framework.

## 🔑 Core Principles

1. **Governance ≠ Control**: Declare boundaries & constraints. NEVER dictate execution flow, reasoning, or tool order.
2. **Agent Autonomy First**: Agents are free to plan/act as long as they satisfy PGC constraints.
3. **Runtime Agnostic**: Schema stays pure. Implementation is delegated to `pgc_adapter`.
4. **Issue-Driven Development**: No Issue, no code change. All features, bug fixes, and docs must be bound to a GitHub Issue with clear DoD (Definition of Done). See `@CONTRIBUTING.md` for the full workflow.

## 📦 Strict Terminology (MANDATORY)

- ✅ Use: `Persona`, `Governance Gate`, `Capability`, `Governance Binding`
- ❌ NEVER Use: `CheckPoint`, `Skill`, `Hook`, `Workflow`, `Trigger`

## 🏗️ Architecture Boundaries

- `pgc_core/`: Pure Pydantic schemas & static validation. Zero runtime deps.
- `pgc_adapter/`: Compiles PGC YAML → target runtime configs.
- 🚫 **NON-GOALS**: No workflow engines, no prompt templates, no tool implementations, no memory/planning logic.

## 📖 Knowledge Base Context

Before generating code, ALWAYS reference:

- `@docs/philosophy/pgc-philosophy-v0.1.md` (Constitution & Mindset)
- `@docs/spec/pgc-spec-v0.3.md` (Schema, Fields & Validation Rules)
- `@docs/runtime-mapping/` (Target Environment Guidelines)
- `@CONTRIBUTING.md` (Issue-Driven Development Workflow & Architecture Red Lines)

**Workflow**: Identify Schema vs Runtime → Reference KB → Output compliant code/config.

## 🔌 Adapter Development Standards

All adapters must follow these rules to ensure consistent version compatibility and rendering behavior.

### Architecture

- Inherit `BaseAdapter` and implement all abstract methods: `render()`, `get_target_runtime()`, `get_target_runtime_version()`, `get_supported_extensions()`
- Adapter code lives under `pgc_adapter/<runtime>/generator.py` with a corresponding `__init__.py`
- Register new adapters in `pgc_adapter/__init__.py`

### Version Compatibility

- Every adapter MUST implement `get_target_runtime_version()` returning `"runtime@X.Y"` format (e.g. `"trae@1.3"`, `"claude-code@1.0"`)
- The version number reflects the **minimum** target runtime version the adapter supports
- `check_runtime_compatibility()` from `pgc_core.validator` is used by `pgc validate` to verify document-adapter version alignment
- When a runtime introduces breaking changes, bump the adapter version and update render logic accordingly
- Old adapter versions remain compatible via SemVer comparison

### Version Upgrade Checklist

When adding a new adapter or updating for a new runtime version:

1. Update `get_target_runtime_version()` to reflect the new minimum supported version
2. Update render logic to support new features/fields introduced in that version
3. Add version compatibility test cases (compatible / version too high / runtime name mismatch / no metadata / empty metadata)
4. Update the corresponding runtime mapping doc under `docs/runtime-mapping/`

### Rendering Rules

- `render()` returns `Dict[str, str]` — keys are relative file paths, values are file contents
- Never perform IO (file writes) inside adapters
- Skip empty sections — do not generate files for empty boundaries/capabilities
- Use `in` assertions in tests, not exact string matching, to avoid fragile tests

### File Naming Convention

- Claude Code: single `CLAUDE.md`
- Trae: multiple files under `.trae/rules/` with YAML frontmatter
- Future adapters: follow the target runtime's native convention
