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
