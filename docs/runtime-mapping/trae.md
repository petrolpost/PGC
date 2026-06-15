---
runtime: trae
versions: ">=1.3"
status: active
adapter: pgc_adapter.trae.TraeAdapter
---

# PGC → Trae IDE Runtime Mapping

This document explains how PGC (Persona-Governance-Capability) concepts map to Trae IDE's native rule file format, and how the `TraeAdapter` translates your governance contract into `.trae/rules/` files.

---

## 1. Mapping Overview

| PGC Element | Trae IDE Feature | Mechanism |
|-------------|-----------------|-----------|
| **Persona** | Rule file with `alwaysApply: true` | `.trae/rules/persona-<id>.md` |
| **Persona.negative_boundaries** | Boundaries rule file | `.trae/rules/boundaries.md` with `NEVER:` directives |
| **GovernanceGate** | Governance rule file | `.trae/rules/governance.md` table row |
| **GovernanceBinding** | Authority + violation policy | Authority level and On Violation column |
| **GovernanceAuthority** | Violation behavior | `block` → "STOP and ask for human review" |
| **Capability** | Capability rule file | `.trae/rules/capabilities.md` with `alwaysApply: false` |

---

## 2. Detailed Mapping

### 2.1 Persona → Persona Rule File

Each PGC Persona generates a dedicated rule file under `.trae/rules/`. The file uses YAML frontmatter with `alwaysApply: true` to ensure the persona definition is always active.

**PGC Source:**

```yaml
personas:
  - id: code-reviewer
    name: Code Reviewer
    responsibilities:
      - 审查代码质量
      - 检查安全漏洞
    output_target: pull-request-review
```

**Generated `.trae/rules/persona-code-reviewer.md`:**

```markdown
---
alwaysApply: true
---

# Code Reviewer (`code-reviewer`)

## Responsibilities

- 审查代码质量
- 检查安全漏洞

## Output Target

pull-request-review
```

### 2.2 Negative Boundaries → Boundaries Rule File

All personas' negative boundaries are consolidated into a single `boundaries.md` file with `alwaysApply: true`. If no boundaries exist, this file is **not generated**.

**Generated `.trae/rules/boundaries.md`:**

```markdown
---
alwaysApply: true
---

# Absolute Boundaries

> **NEVER** violate these boundaries under any circumstances.

- **[Code Reviewer]** NEVER: 直接修改代码
- **[Code Reviewer]** NEVER: 跳过安全检查
```

### 2.3 Governance Gate + Binding → Governance Rule File

Governance rules are rendered into `governance.md` with `alwaysApply: true`.

**Generated `.trae/rules/governance.md`:**

```markdown
---
alwaysApply: true
---

# Governance Rules

| Rule | Gate | Authority | On Violation |
|------|------|-----------|-------------|
| 提交前质量检查 | `pre-commit-quality` | strict | block |

> When a STRICT rule is violated: **STOP and ask for human review.**
```

### 2.4 Capability → Capability Rule File

Capabilities use `alwaysApply: false` with a `description` field, so they are loaded only when relevant. If no capabilities exist, this file is **not generated**.

**Generated `.trae/rules/capabilities.md`:**

```markdown
---
alwaysApply: false
description: "When using or invoking capabilities defined in the PGC governance contract"
---

# Capabilities

| Capability | Owner | Description |
|-----------|-------|-------------|
| `static-analysis` | code-reviewer | 静态代码分析能力 |
```

---

## 3. Trae IDE Frontmatter Fields

Trae IDE rule files support the following YAML frontmatter fields:

| Field | Type | Description |
|-------|------|-------------|
| `alwaysApply` | boolean | `true` = rule is always active; `false` = loaded on demand |
| `description` | string | Description shown in Trae's rule panel (used when `alwaysApply: false`) |
| `globs` | string | File pattern to match for conditional activation (not used by PGC currently) |

---

## 4. Version Notes

- **v1.3+**: Introduced `alwaysApply`, `description`, `globs` frontmatter fields. This is the minimum version supported by `TraeAdapter`.
- Earlier versions of Trae IDE may not support rule files with frontmatter.

---

## 5. Design Rationale

### Why separate files instead of a single file?

Trae IDE loads each `.trae/rules/*.md` file independently. Separating personas, boundaries, governance, and capabilities into individual files allows:

1. **Selective loading**: Capabilities use `alwaysApply: false`, reducing noise
2. **Modularity**: Adding/removing a persona doesn't affect other rules
3. **Clarity**: Each file has a single responsibility

### Why `alwaysApply: true` for boundaries and governance?

Boundaries and governance rules are **non-negotiable constraints** — they must be active at all times, regardless of context. Using `alwaysApply: true` ensures they are never bypassed.
