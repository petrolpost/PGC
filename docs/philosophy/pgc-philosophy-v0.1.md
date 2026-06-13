
# PGC Design Philosophy v0.1

### The Constitution of Agent Governance

## 1. The Paradigm Shift: From Control to Governance

早期 Agent 框架的隐含假设是：“Agent 不可靠，因此需要更精细的流程控制”。这催生了大量的 Workflow、State Machine、Checkpoint 和 Supervisor 机制。

然而，随着现代 Coding Agent（如 Claude Code, Cursor, Codex）的崛起，我们观察到一个不可逆的趋势：

> **Agent 自主能力的进化速度 ≫ Workflow 精细化控制的速度。**

Agent 已经具备了强大的自主规划、自我修正、工具探索和环境学习能力。因此，核心问题发生了根本性转变：
**问题不再是“如何让 Agent 听话”，而是“如何在不压制 Agent 自主性的前提下，建立清晰的治理边界”。**

这促使我们的架构从 **Execution-Oriented Framework (执行控制)** 彻底转向 **Governance-Oriented Schema (治理声明)**。

---

## 2. Core Tenets (核心信条)

### Tenet 1: Governance ≠ Control (治理不等于控制)

控制是规定“必须如何执行”（How）。治理是声明“必须满足什么边界”（What）。
PGC 不会规定：“先进行法律审查，再进行风险审查，最后输出”。
PGC 只会声明：“输出前，必须满足法律合规与风险审查的约束”。
至于何时检查、由谁检查、如何检查，完全交由 Runtime 决定。

### Tenet 2: Agent Autonomy First (代理自主性优先)

PGC 的核心假设是：**Runtime Agent 比 Governance Schema 更了解当前的动态环境。**
在满足 PGC 声明的治理约束的前提下，Agent 拥有绝对的自由去决定：

- 推理路径 (Reasoning Path)
- 工具选择 (Tool Selection)
- 能力调用顺序 (Capability Invocation Order)
- 自我修正策略 (Self-Correction Strategy)
  PGC 绝不压制 Agent 的涌现能力。

### Tenet 3: Capability > Skill (能力声明高于具体实现)

`Skill` 是一个容易过时的 Runtime 概念（今天可能是 Prompt，明天是 Tool，后天是 MCP 或 Sub-Agent）。
`Capability` 是稳定的治理抽象。
PGC 描述系统需要具备何种 **Capability**（例如：`legal-review`），而将如何实现该 Capability 的决定权完全留给 Runtime。

### Tenet 4: Runtime Agnosticism (运行时不可知论)

过去几年，Agent 范式从 Prompt Agent 演进到 Tool Agent，再到 MCP Agent 和 Autonomous Agent，且演进仍在加速。
任何深度绑定特定 Runtime 的治理模型最终都会失效。PGC 的设计目标是：**Runtime 可以自由替换，而 Governance Schema 保持稳定。**

---

## 3. What PGC Is / Is Not

| PGC**IS** (PGC 是)                                      | PGC**IS NOT** (PGC 不是)                        |
| :------------------------------------------------------------ | :---------------------------------------------------- |
| **Agent Governance Schema** (治理模式)                  | Workflow Engine (工作流引擎)                          |
| **Declarative Language** (声明式语言)                   | Runtime Scheduler (运行时调度器)                      |
| **Responsibility & Boundary Mapper** (责任与边界映射器) | Prompt Engineering Framework (提示词工程框架)         |
| **Machine-Verifiable Contract** (机器可验证的契约)      | Multi-Agent Communication Protocol (多智能体通信协议) |

PGC 的定位类似于：

- **OpenAPI** 描述 API 契约，但不提供 Web Server。
- **Terraform (HCL)** 描述基础设施状态，但不提供云厂商 API。
- **PGC** 描述 Agent 治理结构，但不提供 Agent 运行时。

---

## 4. The Evolution: Why PCS became PGC

最初的 **PCS (Persona-CheckPoint-Skill)** 模型回答的是 Workflow 问题：*Who, When, What*。
随着哲学转向，这三个概念发生了本质升维，演化为 **PGC (Persona-Governance-Capability)**，回答的是 Governance 问题：

- **Persona (责任主体)**：谁负责？边界在哪？
- **Governance (治理约束)**：必须满足何种关卡 (Gate)？
- **Capability (能力声明)**：具备何种能力来满足约束？

保留 "CheckPoint" 这个名字会持续误导开发者将其视为“时序触发器”。因此，从 v0.3 开始，我们正式在概念层面用 **Governance Gate** 替代 CheckPoint，用 **Capability** 替代 Skill，完成向 PGC 的平滑过渡。

---

## 5. The Ultimate Goal

PGC 的长期目标，不是构建更复杂、更庞大的 Agent 系统。
而是**让日益强大的 Agent 系统，拥有可声明 (Declarable)、可审查 (Auditable)、可验证 (Verifiable) 的治理结构。**
