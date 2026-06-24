# 🤖 PGC Project Directive

You are the core architect for **PGC (Persona-Governance-Capability)**.
PGC is an **Agent Governance Schema**, NOT an execution/runtime framework.

---

## Core Rules [Always-on]

以下规则始终生效，无需额外加载。

### Core Principles

1. **Governance ≠ Control**: Declare boundaries & constraints. NEVER dictate execution flow, reasoning, or tool order.
2. **Agent Autonomy First**: Agents are free to plan/act as long as they satisfy PGC constraints.
3. **Runtime Agnostic**: Schema stays pure. Implementation is delegated to `pgc_adapter`.
4. **Issue-Driven Development**: No Issue, no code change. All features, bug fixes, and docs must be bound to a GitHub Issue with clear DoD (Definition of Done). See `.agent/rules/issue-driven.md` for the lifecycle rules and `tgs/README.md` for this repository's external TGS adoption pointer.

### Key Definitions

| Term | Definition | Prohibited |
|------|-----------|------------|
| **Persona** | Agent 的身份与行为约束 | ❌ Character / Role |
| **Governance Gate** | 决策检查点 | ❌ CheckPoint / Rule |
| **Capability** | 可声明的能力单元 | ❌ Feature / Plugin |
| **Governance Binding** | Persona ↔ Gate/Capability 的关联 | ❌ Link / Mapping |

### Architecture Boundaries

- `pgc_core/` — Pure Pydantic schemas & static validation. Zero runtime deps.
- `pgc_adapter/` — Compiles PGC YAML → target runtime configs. Never reverse-depends on `pgc_core`.
- 🚫 **NON-GOALS**: No workflow engines, no prompt templates, no tool implementations, no memory/planning logic.

### Knowledge Base

Before generating code, ALWAYS reference:

- `docs/philosophy/pgc-philosophy-v0.1.md` — Constitution & Mindset
- `docs/spec/pgc-spec-v0.3.md` — Schema, Fields & Validation Rules
- `docs/runtime-mapping/` — Target Environment Guidelines
- `CONTRIBUTING.md` — Issue-Driven Development Workflow & Architecture Red Lines

**Workflow**: Identify Schema vs Runtime → Reference KB → Output compliant code/config.

---

## Domain Rules [On-demand]

以下规则按场景加载，遇到相关任务时读取对应文件。

| Scenario | Rule File |
|----------|-----------|
| 架构详细规范与术语完整定义 | `.agent/rules/architecture.md` |
| Adapter 开发 | `.agent/rules/adapter.md` |
| Issue 驱动开发流程 | `.agent/rules/issue-driven.md` |
| TGS 采用关系 | `tgs/README.md` |
| 技术问题排查 | `.agent/solutions/README.md` |
