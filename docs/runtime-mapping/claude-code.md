---
runtime: claude-code
versions: ">=1.0"
status: active
adapter: pgc_adapter.claude.ClaudeCodeAdapter
---

# PGC → Claude Code Runtime Mapping

This document explains how PGC (Persona-Governance-Capability) concepts map to Claude Code's native mechanisms, and how the `ClaudeCodeAdapter` translates your governance contract into an executable `CLAUDE.md`.

---

## 1. Mapping Overview

| PGC Element | Claude Code Feature | Mechanism |
|-------------|-------------------|-----------|
| **Persona** | Role definition in `CLAUDE.md` | `## Role & Responsibilities` section |
| **Persona.negative_boundaries** | Hard constraints | `## Absolute Boundaries` with `NEVER:` directives |
| **GovernanceGate** | Governance rule entry | `## Governance Rules` table row |
| **GovernanceBinding** | Authority + violation policy | Authority level and On Violation column |
| **GovernanceAuthority** | Violation behavior | `block` → "STOP and ask for human review" |
| **Capability** | Declared ability | `## Capabilities` table |
| **Persona.output_target** | Deliverable destination | `## Output Targets` table |

---

## 2. Detailed Mapping

### 2.1 Persona → Role & Responsibilities

A PGC Persona defines **who** is accountable and **what** they are responsible for. In Claude Code, this becomes a structured role definition that the agent uses to frame its behavior.

**PGC Source:**

```yaml
personas:
  - id: code-reviewer
    name: Code Reviewer
    responsibilities:
      - 审查代码质量
      - 检查安全漏洞
      - 确保测试覆盖率
    negative_boundaries:
      - 直接修改代码
      - 跳过安全检查
    output_target: pull-request-review
```

**Generated CLAUDE.md:**

```markdown
## Role & Responsibilities

### Code Reviewer (`code-reviewer`)

- 审查代码质量
- 检查安全漏洞
- 确保测试覆盖率
```

### 2.2 Negative Boundaries → Absolute Boundaries

PGC's `negative_boundaries` are the most critical safety mechanism. They define **absolute prohibitions** — actions the agent must never take under any circumstances. Claude Code treats these as hard system constraints.

**Generated CLAUDE.md:**

```markdown
## Absolute Boundaries

> **NEVER** violate these boundaries under any circumstances.

- **[Code Reviewer]** NEVER: 直接修改代码
- **[Code Reviewer]** NEVER: 跳过安全检查
```

> **Why this matters:** Without PGC, boundaries are often implicit or scattered across documentation. PGC makes them explicit, machine-verifiable, and enforced at the adapter level.

### 2.3 Governance Gate + Binding → Governance Rules

A GovernanceGate defines **what** constraint exists. A GovernanceBinding assigns **who** is responsible and **how strictly** it must be enforced. Together they become a governance rule table.

**PGC Source:**

```yaml
governance_gates:
  - id: pre-commit-quality
    type: quality
    description: 提交前质量检查

governance_bindings:
  - gate_id: pre-commit-quality
    persona_id: code-reviewer
    capability_id: static-analysis
    authority_level: strict

governance_authority:
  default_violation_policy: block
```

**Generated CLAUDE.md:**

```markdown
## Governance Rules

| Rule | Gate | Authority | On Violation |
|------|------|-----------|-------------|
| 提交前质量检查 | `pre-commit-quality` | strict | block |

> When a STRICT rule is violated: **STOP and ask for human review.**
```

#### Authority Levels

| Authority Level | Behavior |
|----------------|----------|
| `strict` | Must be satisfied. Violation → STOP and ask for human review |
| `advisory` | Should be satisfied. Violation → Log warning only |

#### Violation Policies

| Policy | Effect in CLAUDE.md |
|--------|-------------------|
| `block` | Agent must halt and request human intervention |
| `warn` | Agent logs a warning but may continue |
| `log` | Agent silently records the violation |

### 2.4 Capability → Capabilities Table

Capabilities declare **what abilities** are available and **who owns** them. This prevents capability drift where an agent assumes abilities it shouldn't have.

**PGC Source:**

```yaml
capabilities:
  - id: static-analysis
    owner_persona: code-reviewer
    description: 静态代码分析能力
```

**Generated CLAUDE.md:**

```markdown
## Capabilities

| Capability | Owner | Description |
|-----------|-------|-------------|
| `static-analysis` | code-reviewer | 静态代码分析能力 |
```

### 2.5 Output Target → Output Targets Table

Each Persona's deliverable destination is made explicit, preventing output misrouting.

**Generated CLAUDE.md:**

```markdown
## Output Targets

| Persona | Target |
|---------|--------|
| Code Reviewer | pull-request-review |
```

---

## 3. Before PGC vs After PGC

### Before PGC: Implicit Governance

```markdown
# CLAUDE.md (hand-written)

You are a code reviewer. Please review code for quality and security.
Don't modify code directly. Make sure to check tests.
```

**Problems:**
- Boundaries are vague ("Don't modify code directly" — is it a suggestion or a hard rule?)
- No enforcement mechanism — the agent may "forget" constraints
- No traceability — who is responsible for what?
- No authority levels — all rules appear equally important
- No violation policy — what happens when a rule is broken?

### After PGC: Explicit, Enforced Governance

```markdown
# CLAUDE.md

> Auto-generated by PGC (Persona-Governance-Capability) Adapter for Claude Code.
> DO NOT edit manually — regenerate from your .pgc.yaml source.

---

## Role & Responsibilities

### Code Reviewer (`code-reviewer`)

- 审查代码质量
- 检查安全漏洞
- 确保测试覆盖率

## Absolute Boundaries

> **NEVER** violate these boundaries under any circumstances.

- **[Code Reviewer]** NEVER: 直接修改代码
- **[Code Reviewer]** NEVER: 跳过安全检查

## Governance Rules

| Rule | Gate | Authority | On Violation |
|------|------|-----------|-------------|
| 提交前质量检查 | `pre-commit-quality` | strict | block |

> When a STRICT rule is violated: **STOP and ask for human review.**

## Output Targets

| Persona | Target |
|---------|--------|
| Code Reviewer | pull-request-review |

## Capabilities

| Capability | Owner | Description |
|-----------|-------|-------------|
| `static-analysis` | code-reviewer | 静态代码分析能力 |
```

**Improvements:**
- Boundaries are **absolute** — marked with `NEVER` and enforced by authority level
- Responsibilities are **enumerated** — no ambiguity about scope
- Violation policy is **explicit** — agent knows to STOP on strict violations
- Governance is **traceable** — every rule links back to a gate, persona, and capability
- Configuration is **regenerable** — edit `.pgc.yaml`, re-run adapter, CLAUDE.md updates

---

## 4. Usage

### 4.1 Generate CLAUDE.md from PGC YAML

```python
from pgc_adapter.claude import ClaudeCodeAdapter
from pgc_core.model import PGCDocument
import yaml

# Load your PGC document
with open("agent.pgc.yaml", encoding="utf-8") as f:
    data = yaml.safe_load(f)

doc = PGCDocument(**data)

# Render to CLAUDE.md
adapter = ClaudeCodeAdapter()
result = adapter.render(doc)

# Write to file
with open("CLAUDE.md", "w", encoding="utf-8") as f:
    f.write(result["CLAUDE.md"])
```

### 4.2 Using the CLI

```bash
# Initialize a new PGC project
pgc init ./my-project

# Validate your PGC document
pgc validate ./my-project/agent.pgc.yaml

# Generate CLAUDE.md (future: pgc export --runtime claude-code)
```

---

## 5. Design Rationale

### Why CLAUDE.md?

Claude Code reads `CLAUDE.md` as a **system-level instruction file**. It has the highest priority in shaping agent behavior — higher than user messages. This makes it the ideal target for governance constraints that must not be overridden.

### Why not `.cursorrules` or other formats?

Each runtime has its own configuration format and priority model. PGC's adapter architecture ensures that governance semantics are preserved across runtimes. The same `.pgc.yaml` source can generate:

- `CLAUDE.md` for Claude Code (via `ClaudeCodeAdapter`)
- `.cursorrules` for Cursor (future `CursorAdapter`)
- Custom formats for other runtimes

### Why "NEVER" directives?

Claude Code responds strongly to absolute language. "NEVER" creates a hard constraint that is significantly harder for the agent to rationalize away than softer language like "avoid" or "should not."

---

## 6. Limitations & Future Work

| Limitation | Plan |
|-----------|------|
| No `mcp_tools_schema.json` generation yet | Future: generate MCP tool schema from Capabilities |
| No incremental update | Future: diff-based update to preserve manual additions |
| Single-runtime only | Future: `pgc export --runtime <name>` with adapter registry |
| No runtime feedback loop | Future: runtime events → PGC validation → adapter re-render |
