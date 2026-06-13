# Architecture & Terminology

This file contains the complete architecture boundaries and terminology specifications for the PGC project.

## Terminology (MANDATORY)

### Approved Terms

| Term | Definition | Context |
|------|-----------|---------|
| **Persona** | Agent 的身份与行为约束 | PGC 文档的核心实体，定义 Agent 是谁、如何行动 |
| **Governance Gate** | 决策检查点 | 在关键决策节点施加约束，确保行为合规 |
| **Capability** | 可声明的能力单元 | Agent 可使用的工具、技能或权限的声明式描述 |
| **Governance Binding** | Persona ↔ Gate/Capability 的关联 | 将 Persona 与 Gate/Capability 绑定，形成治理闭环 |
| **PGCDocument** | PGC 文档的根容器 | 包含 personas、governance_gates、capabilities、governance_bindings |

### Prohibited Terms

| Prohibited | Use Instead | Reason |
|-----------|-------------|--------|
| CheckPoint | Governance Gate | "CheckPoint" 暗示流程控制，违背 Governance ≠ Control |
| Skill | Capability | "Skill" 暗示执行逻辑，PGC 只声明能力 |
| Hook | Governance Gate | "Hook" 暗示回调机制，PGC 只声明约束 |
| Workflow | Governance Binding | "Workflow" 暗示执行流程，PGC 只声明关联 |
| Trigger | Governance Gate | "Trigger" 暗示事件驱动，PGC 只声明检查点 |
| Character / Role | Persona | 统一术语，避免歧义 |
| Feature / Plugin | Capability | 统一术语，避免歧义 |
| Link / Mapping | Governance Binding | 统一术语，避免歧义 |

## Architecture Boundaries

### Module Structure

```
pgc_core/          Pure data models + validation, zero runtime deps
  model.py         Pydantic schemas (Persona, GovernanceGate, Capability, ...)
  validator.py     Static validation (check_runtime_compatibility, ...)

pgc_adapter/       Compilers: PGC YAML → target runtime configs
  base.py          BaseAdapter abstract class
  claude/          ClaudeCodeAdapter → CLAUDE.md
  trae/            TraeAdapter → .trae/rules/*.md
```

### Dependency Rules

- `pgc_core/` has **zero** runtime dependencies — only Pydantic + standard lib
- `pgc_adapter/` depends on `pgc_core/`, **never** the reverse
- Adapters never import from each other
- `pgc_adapter/` performs **no IO** — `render()` returns `Dict[str, str]`, callers handle writes

### NON-GOALS

PGC explicitly does NOT provide:

- Workflow engines or execution runtimes
- Prompt templates or conversation managers
- Tool implementations or API clients
- Memory systems or planning logic
- Any runtime behavior — PGC is a **schema**, not a framework

## Rule System Structure

The `.agent/` directory contains project-level rules and resources:

```
.agent/
  rules/          Domain-specific rules (on-demand loading)
  solutions/      Technical problem solutions (on-demand loading)
  mcp/            MCP configurations (reserved)
  scripts/        Helper scripts (reserved)
  skills/         Skill definitions (reserved)
  config/         Configuration files (reserved)
```

All content under `.agent/` is version-controlled and IDE-agnostic.

### Loading Strategy

- **Always-on** rules live in `Agent.md` (project root) — loaded at Agent startup
- **On-demand** rules live in `.agent/rules/` — loaded when relevant tasks arise
- `Agent.md` contains a Domain Rules index table pointing to on-demand files
