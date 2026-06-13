# PGC Specification v0.3

### Governance-First Edition

**Status**: Draft
**Replaces**: PCS v0.2
**Guiding Philosophy**: [PGC Design Philosophy v0.1](../philosophy/pgc-philosophy-v0.1.md)

---

## 1. Introduction

PGC (Persona-Governance-Capability) is an **Agent Governance Schema**.
It provides a declarative, machine-verifiable language to describe the structural constraints, responsibility boundaries, and capability assignments of an Agent system.

PGC **does not** define execution flows, reasoning paths, or runtime scheduling. It strictly defines **what** must be governed, leaving **how** to the Runtime environment.

---

## 2. Core Concepts

The PGC model decomposes an Agent system into three orthogonal dimensions:

| Dimension                | Element                   | Core Question                         |
| :----------------------- | :------------------------ | :------------------------------------ |
| **Responsibility** | **Persona**         | Who is accountable?                   |
| **Constraint**     | **Governance Gate** | What boundaries must be respected?    |
| **Ability**        | **Capability**      | What abstract abilities are declared? |

These elements are linked by **Governance Bindings**, which declare responsibility assignments without dictating execution mechanics.

---

## 3. Schema Definition

All PGC declarations must be structured (e.g., YAML). The following defines the core schema entities.

### 3.1 Persona (Responsibility Subject)

A Persona defines a logical role and its boundaries of accountability.

```yaml
persona:
  id: string             # Unique identifier (e.g., 'code-reviewer')
  name: string           # Human-readable name
  responsibilities:      # List of explicit duties
    - string       
  negative_boundaries:   # Explicit list of forbidden actions (Crucial for drift prevention)
    - string       
  output_target: string  # Where this persona's deliverables are directed
```

### 3.2 Governance Gate (The Constraint)

**A Governance Gate declares a specific constraint that must be satisfied. It is ****not** a temporal trigger or a workflow node.

```yaml
governance_gate:
  id: string             # Unique identifier (e.g., 'output-quality-gate', 'legal-compliance-gate')
  type: string           # Category: 'security' | 'quality' | 'compliance' | 'business_rule'
  description: string    # Human-readable definition of the constraint
```

### 3.3 Capability (The Abstract Ability)

A Capability declares an abstract ability required to satisfy a Governance Gate. It does not specify the implementation (e.g., Tool, MCP, Prompt, Sub-Agent).

```yaml
capability:
  id: string             # Unique identifier (e.g., 'static-code-analysis')
  owner_persona: string  # Reference to the Persona that owns/provides this capability
  description: string    # Human-readable definition of what this capability achieves
  
```

3.4 Governance Binding (The Assignment)
A Binding declares that a specific Persona is responsible for satisfying a specific Governance Gate, utilizing a specific Capability.

```yaml
governance_binding:
  gate_id: string        # Reference to the Governance Gate
  persona_id: string     # Reference to the responsible Persona
  capability_id: string  # Reference to the Capability used to satisfy the gate
  authority_level: string # 'strict' (block on violation) | 'advisory' (warn/log)
```

### 3.5 Governance Authority (The Meta-Policy)

Defines the global or gate-level policies for handling Governance Drift (violations).

```yaml
governance_authority:
  default_violation_policy: string # Global fallback: 'block' | 'warn' | 'log'
  gate_overrides:
    - gate_id: string
      violation_policy: string     # Specific policy for a specific gate
```

## 4. Validation Rules

**A valid PGC document must pass the following static analysis checks:**

1. **Referential Integrity** **: All IDs referenced in Bindings (**`gate_id`, `persona_id`, `capability_id`) must exist in the document.
2. **Capability Ownership** **: The **`owner_persona` declared in a Capability **must match** the `persona_id` in the Governance Binding that uses it. (Prevents responsibility mismatch).
3. **Gate Coverage** **: Every defined **`governance_gate`**must** have at least one valid `governance_binding`. (No unowned gates).
4. **Boundary Consistency** **: A Persona's declared **`capabilities` must not logically violate its own `negative_boundaries`.

---

## 5. Non-Goals (Strictly Out of Scope)

**To maintain its purity as a Governance Schema, PGC explicitly ****does not** provide, define, or manage:

* **❌ ** **Execution Mechanics** **: Hooks, triggers, event loops, or schedulers.**
* **❌ ** **Workflow Topology** **: DAGs, state machines, or sequential flow definitions.**
* **❌ ** **Runtime Implementations** **: Prompts, MCP servers, Tool definitions, or API calls.**
* **❌ ** **Agent Cognition** **: Reasoning paths, memory management, or planning algorithms.**

---

## 6. Runtime Mapping (Conceptual)

**PGC is designed to be compiled or mapped into various Runtime environments. The Schema itself remains untouched.**

| **PGC Element**     | **Conceptual Mapping Examples (Depending on Runtime)**                    |
| ------------------------- | ------------------------------------------------------------------------------- |
| **Persona**         | **System Prompt Role,**`.cursorrules`Profile, Sub-Agent Instance        |
| **Governance Gate** | **Linter Rule, Policy Engine Check, Human Review Step, Graph Node Guard** |
| **Capability**      | **MCP Tool, Bash Script, Python Function, External API**                  |
| **Binding**         | **Tool Pre-condition, Middleware Interceptor, Conditional Edge Routing**  |
| **Authority**       | **CI/CD Gatekeeper, IDE Error Highlighter, Exception Handler**            |

---

## 7. Example: A Simple Coding Agent Governance
```yaml
personas:
  - id: developer
    name: Core Developer
    responsibilities: ["implement features", "fix bugs"]
    negative_boundaries: ["modify core database schema without approval", "commit code without running tests"]
    output_target: source_code_repository

  - id: quality-assurance
    name: QA Guardian
    responsibilities: ["ensure code quality", "enforce security standards"]
    negative_boundaries: ["write business logic"]
    output_target: review_logs

governance_gates:
  - id: pre-commit-quality-gate
    type: quality
    description: Code must pass static analysis and have >80% test coverage before committing.
  - id: schema-mutation-gate
    type: security
    description: Any change to database schema requires explicit human authorization.

capabilities:
  - id: run-linter-and-tests
    owner_persona: quality-assurance
    description: Execute static code analysis and unit test suites.
  - id: verify-schema-permissions
    owner_persona: quality-assurance
    description: Check if the current operation has explicit human approval for schema changes.

governance_bindings:
  - gate_id: pre-commit-quality-gate
    persona_id: quality-assurance
    capability_id: run-linter-and-tests
    authority_level: strict

  - gate_id: schema-mutation-gate
    persona_id: quality-assurance
    capability_id: verify-schema-permissions
    authority_level: strict

governance_authority:
  default_violation_policy: block
```

