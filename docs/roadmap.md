# PGC Roadmap

本路线图旨在指导 PGC (Persona-Governance-Capability) 从核心契约层向生态适配层的演进。
所有里程碑均严格遵循《PGC Design Philosophy v0.1》，坚持 **Governance-First** 与 **Runtime Agnostic**。

---

## 🟢 Phase 1: Core Foundation (Layer 0) - *Completed*

**目标**：夯实治理契约基石，确保 Schema 的严谨性与机器可验证性。

- [X] **PGC Spec v0.3 定稿**：完成从 Execution 到 Governance 的哲学转向与术语净化。
- [X] **Pydantic Models**：实现 `Persona`, `GovernanceGate`, `Capability`, `GovernanceBinding` 核心模型。
- [X] **Validation Engine**：实现引用完整性、能力归属校验、关卡覆盖检查。
- [X] **CLI Tool (`pgc-core`)**：完善 `pgc validate` (单文件/目录) 与 `pgc init` (生成标准模板) 命令。
- [X] **Test Coverage**：核心模型与验证规则 100% 单元测试覆盖。

## 🟢 Phase 2: Runtime Proof (Layer 1) - *Completed* (v0.3)

**目标**：通过主流 AI IDE 的 Adapter，证明 PGC 在真实环境中的"无感控制"价值。

- [X] **Adapter Architecture**：定义 `BaseAdapter` 抽象接口与渲染生命周期。
- [X] **Claude Code Adapter**：实现 PGC YAML 到 `CLAUDE.md` (角色/边界) 的编译。
- [X] **Adapter Runtime Versioning**：实现运行时版本化机制，支持 SemVer 兼容性检查。
- [X] **Runtime Mapping Docs**：完善 Claude Code / Trae 映射文档，建立版本化命名规范。
- [X] **Trae Adapter**：实现 PGC YAML 到 Trae IDE 规则文件（`.trae/rules/`）的编译。
- [X] **Example Showcase**：提供完整的 Coding Agent 防漂移治理案例，对比使用 PGC 前后的 Agent 行为差异。
- [X] **CLI Bug Fix & Cleanup**：修复 validate NameError，清理空文件，添加 pytest 配置。
- [X] **`pgc render` Command**：添加 CLI 渲染命令，支持 `pgc render <yaml> --adapter <name> [--output <dir>]`。

## 🟡 Phase 2.5: Dogfooding (Layer 1 Validation) - *In Progress*

**目标**：用 PGC 管理自身，验证端到端流程的可用性，发现并修复实际使用中的问题。

- [ ] **Self-Governance**：为 PGC 项目编写 `.pgc.yaml`，用 `pgc render` 生成运行时配置，对比手写规则。
- [ ] **Rule System Refinement**：基于 dogfooding 结果，调整 Always-on / On-demand 规则分层。
- [ ] **Stability Fixes**：解决 `.git` 目录反复丢失等稳定性问题，归档解决方案。

## 🔵 Phase 3: Workflow Integration (Layer 1 Advanced) - *Deferred*

> **Note**: Phase 3 将在 Phase 2.5 Dogfooding 完成且 Coding Agent 磨合清晰后启动。

**目标**：将治理契约无缝注入到复杂的编排框架中，实现“声明即路由”。

- [ ] **LangGraph Adapter**：将 PGC 编译为 `StateGraph` 骨架、Governance Node 模板与 Conditional Edges。
- [ ] **AutoGen / CrewAI Adapter**：映射 PGC Persona 到多智能体拓扑中的 Agent 角色与权限边界。
- [ ] **Policy-as-Code Export**：支持将 Governance Gates 导出为 OPA (Open Policy Agent) Rego 策略文件，对接企业级合规系统。

## 🟣 Phase 4: Runtime Observation (Layer 2)

**目标**：为缺乏原生治理能力的自建框架提供运行时保障。

- [ ] **Interception Engine**：提供 Python/TS 装饰器/中间件，在 Tool 调用前后强制注入 Governance 检查。
- [ ] **Drift Observer**：记录 Agent 运行时的违规行为（如绕过 Gate、越权调用 Capability），生成漂移报告。
- [ ] **Fallback Arbitrator**：当 Runtime 发生治理冲突时，提供基于 `GovernanceAuthority` 的默认降级/阻断策略。

## 🟤 Phase 5: Ecosystem & Visualization (Layer 3 & Beyond)

**目标**：降低 PGC 的使用门槛，建立社区生态。

- [ ] **PGC Studio (Web)**：可视化编辑 Persona、绘制 Governance Gate 拓扑图、实时验证 Schema。
- [ ] **VS Code / Cursor Extension**：在 IDE 中提供 `.pgc.yaml` 的语法高亮、自动补全与实时错误提示。
- [ ] **Community Adapters**：建立标准，支持社区贡献针对 Dify, Coze, OpenHands 等平台的 Adapter。
