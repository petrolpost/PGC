# Issue #16: 重构规则系统 — .agent/ 目录与 Issue 驱动开发规则

## 1. 需求分析

### 1.1 背景

在 #13 的开发过程中，暴露了当前规则系统的结构性问题：

1. **Agent.md 职责过重**：同时承载了核心定义、架构边界、知识库导航、Adapter 开发规范等，73 行内容膨胀，难以维护和导航
2. **规则散落**：项目规则、开发规范、问题解决方案没有统一的存放位置和索引机制
3. **问题方案无沉淀**：开发中遇到的技术问题（如 git 孤立分支、sandbox 限制、GH_TOKEN scope 不足）解决后没有归档，下次遇到同样问题需要重新排查
4. **Issue 驱动开发流程不够明确**：CONTRIBUTING.md 有基本流程，但缺少具体的操作规范、常见陷阱和验证检查点
5. **规则与代码耦合**：Agent.md 中混合了项目治理规则（通用）和领域特定规范（Adapter），缺乏分层

### 1.2 目标

1. 将 Agent.md 重构为**结构清晰的入口**，保留核心定义和导航，便于模块化优化（≤ 250 行）
2. 建立 `.agent/` 目录体系，分层存放项目规则、技术方案、配置等
3. 将现有 Agent.md 中的具体规范迁移到 `.agent/rules/` 下的独立文件
4. 建立技术问题解决方案归档机制，沉淀开发经验
5. 新增 Issue 驱动开发规则，覆盖完整生命周期

### 1.3 约束

- **通用性**：规则系统是项目级的，不依赖任何特定 IDE 的功能（如 Trae 的 `.trae/rules/` 或 Claude 的 `CLAUDE.md`）
- **自洽性**：新的规则系统必须在其自身框架内运作（即本 Issue 的开发也必须遵循新规则）
- **向后兼容**：Agent.md 作为入口文件，其路径不变（仍是项目根目录的 `Agent.md`）
- **导航可达**：从 Agent.md 出发，通过直接或间接引用，必须能到达每个规则文件
- **不修改 CONTRIBUTING.md**：CONTRIBUTING.md 是 GitHub 社区规范入口，保持不变；Issue 驱动开发的增强规则放在 `.agent/rules/issue-driven.md`
- **不修改 .gitignore**：`.agent/` 目录是项目规则的一部分，必须纳入版本控制

### 1.4 设计原则

| 原则       | 说明                                     |
| ---------- | ---------------------------------------- |
| 入口结构化 | Agent.md 结构清晰、模块化，便于维护和扩展（≤ 250 行） |
| 分层加载 | 核心规则（always-on）在 Agent.md 中直接生效，领域规则（on-demand）按需从 `.agent/rules/` 加载 |
| 单一职责   | 每个规则文件只关注一个领域               |
| 问题可沉淀 | 技术问题解决后必须归档，避免重复排查     |
| 流程可验证 | 每个开发步骤都有验证检查点               |
| IDE 无关   | 规则系统不依赖任何 IDE 特性              |

### 1.5 规则加载策略

规则按生效方式分为两层：

| 层级 | 加载方式 | 存放位置 | 特征 |
|------|----------|----------|------|
| **核心规则** | Always-on，Agent 启动即生效 | Agent.md | 项目身份、核心原则、术语定义、架构边界 — 任何时刻都必须遵守 |
| **领域规则** | On-demand，按场景加载 | `.agent/rules/*.md` | Adapter 开发规范、Issue 驱动流程、特定领域约束 — 仅在相关场景下需要 |

**判断标准**：

- 如果违反该规则会导致项目根本性错误（如混淆 PGC 与运行时框架），则为核心规则
- 如果该规则只在特定开发场景下需要（如写 Adapter 时、处理 Issue 时），则为领域规则
- Agent.md 中的 Navigation 表是领域规则的索引，Agent 按需读取

## 2. 设计方案

### 2.1 目录结构

```
.agent/
  rules/                    # 项目规则
    architecture.md         # 架构边界与术语规范
    adapter.md              # Adapter 开发规范
    issue-driven.md         # Issue 驱动开发规则
  solutions/                # 技术问题解决方案
    README.md               # 索引文件
    git-branch-orphan.md    # 孤立分支问题
    git-sandbox-write.md    # Sandbox 写入限制问题
    gh-token-scope.md       # GH_TOKEN scope 问题
  mcp/                      # MCP 配置（预留，当前为空）
  scripts/                  # 辅助脚本（预留，当前为空）
  skills/                   # Skills 定义（预留，当前为空）
  config/                   # 配置文件（预留，当前为空）
```

### 2.2 Agent.md 重构

**重构前**（73 行，6 个章节）：

- Core Principles
- Strict Terminology
- Architecture Boundaries
- Knowledge Base Context
- Adapter Development Standards（5 个子章节）

**重构后**（目标 ≤ 250 行，结构清晰、模块化）：

Agent.md 分为两大区域：**核心规则（Always-on）**直接生效，**领域规则索引（On-demand）**按需加载。

```markdown
# 🤖 PGC Project Directive

You are the core architect for **PGC (Persona-Governance-Capability)**.
PGC is an **Agent Governance Schema**, NOT an execution/runtime framework.

---

## Core Rules [Always-on]

以下规则始终生效，无需额外加载。

### Core Principles

1. **Governance ≠ Control**
2. **Agent Autonomy First**
3. **Runtime Agnostic**
4. **Issue-Driven Development**

### Key Definitions

| 术语 | 定义 | 禁用 |
|------|------|------|
| Persona | Agent 的身份与行为约束 | ❌ Character/Role |
| Governance Gate | 决策检查点 | ❌ CheckPoint/Rule |
| Capability | 可声明的能力单元 | ❌ Feature/Plugin |
| Binding | Persona ↔ Gate/Capability 的关联 | ❌ Link/Mapping |

### Architecture Boundaries

- `pgc_core/` — 纯数据模型 + 验证，零运行时依赖
- `pgc_adapter/` — 编译器，将 PGC YAML → 运行时配置，禁止反向依赖
- PGC 不执行 Agent，不管理运行时状态

### Knowledge Base

- `docs/philosophy/pgc-philosophy-v0.1.md`
- `docs/spec/pgc-spec-v0.3.md`
- `docs/runtime-mapping/`
- `CONTRIBUTING.md`

---

## Domain Rules [On-demand]

以下规则按场景加载，遇到相关任务时读取对应文件。

| 场景 | 规则文件 |
|------|----------|
| 架构详细规范与术语完整定义 | `.agent/rules/architecture.md` |
| Adapter 开发 | `.agent/rules/adapter.md` |
| Issue 驱动开发流程 | `.agent/rules/issue-driven.md` |
| 技术问题排查 | `.agent/solutions/README.md` |
```

**设计意图**：

- **Always-on 区域**：Agent 启动即生效的核心规则，确保项目基本约束始终被遵守
- **On-demand 区域**：领域规则的索引表，Agent 在遇到相关场景时按需加载
- 这种分层既避免了 Agent.md 过度膨胀，又确保核心规则不需要额外跳转即可生效

### 2.3 规则文件设计

#### 2.3.1 `.agent/rules/architecture.md`

从 Agent.md 迁出的内容：

- Strict Terminology（术语规范）
- Architecture Boundaries（架构边界）
- NON-GOALS

新增内容：

- 规则系统自身说明（.agent/ 目录的作用和结构）

#### 2.3.2 `.agent/rules/adapter.md`

从 Agent.md 迁出的内容：

- Adapter Development Standards 全部 5 个子章节
  - Architecture
  - Version Compatibility
  - Version Upgrade Checklist
  - Rendering Rules
  - File Naming Convention

无新增内容。

#### 2.3.3 `.agent/rules/issue-driven.md`（新增）

覆盖 Issue 驱动开发的完整生命周期：

**Phase 1: Issue 识别与提交**

- 何时需要创建 Issue（功能、Bug、重构、文档）
- Issue 模板：Context / Tasks / DoD
- DoD 必须可验证（测试命令、文件存在性、输出格式）

**Phase 2: Issue 认领与分支创建**

- 认领命令：`gh issue edit <N> --add-assignee "@me"`
- 分支命名：`<type>/<issue-number>-<short-description>`
- **关键检查点**：创建分支后必须验证 `git log` 有历史，否则是孤立分支
- 正确的分支创建流程：
  ```bash
  git checkout main
  git pull
  git checkout -b <branch-name>
  git log --oneline -3  # 验证：必须有历史，不能是 "no commits yet"
  ```

**Phase 3: 开发过程**

- Spec 先行：每个 Issue 必须先写 spec 和测试计划
- Spec 存放：`docs/issues/<issue-number>-<slug>/spec.md` 和 `test-plan.md`
- 开发中的提交规范：Conventional Commits + Issue 编号
- 暂存区检查：提交前 `git status` 确认只有相关文件

**Phase 4: PR 提交与合并**

- PR 描述模板：Summary / Changes / Test Results / Checklist
- PR 必须关联 Issue（`Closes #N`）
- 合并后清理：删除本地和远程分支

### 2.4 技术问题解决方案设计

#### 2.4.1 归档规范

每个解决方案文件遵循统一结构：

```markdown
# <问题标题>

## Problem

<问题描述：现象、错误信息>

## Root Cause

<根因分析>

## Solution

<解决方案：具体操作步骤>

## Verification

<验证步骤：如何确认问题已解决>
```

#### 2.4.2 索引规范

`.agent/solutions/README.md` 按类别分组索引：

```markdown
# Technical Solutions Index

## Git
- [git-branch-orphan.md](git-branch-orphan.md) — 孤立分支问题
- [git-sandbox-write.md](git-sandbox-write.md) — Sandbox 写入限制

## GitHub CLI
- [gh-token-scope.md](gh-token-scope.md) — GH_TOKEN scope 不足
```

#### 2.4.3 首批归档内容

| 文件                     | 问题                                                         | 来源     |
| ------------------------ | ------------------------------------------------------------ | -------- |
| `git-branch-orphan.md` | `git checkout -b` 创建孤立分支（无 commit 历史）           | #13 开发 |
| `git-sandbox-write.md` | trae-sandbox 阻止 .git 目录写入，导致 refs 更新失败          | #13 开发 |
| `gh-token-scope.md`    | GH_TOKEN 缺少 `read:org` scope 导致 `gh auth login` 失败 | #13 开发 |

### 2.5 迁移映射

| 原位置（Agent.md 章节）       | 新位置                           | 加载层级 | 操作                 |
| ----------------------------- | -------------------------------- | -------- | -------------------- |
| Core Principles（4 条）       | Agent.md Core Rules              | Always-on | 保留       |
| Strict Terminology            | Agent.md Key Definitions + `.agent/rules/architecture.md` | Always-on + On-demand | 核心摘要保留 + 详细迁出 |
| Architecture Boundaries       | Agent.md Architecture Boundaries + `.agent/rules/architecture.md` | Always-on + On-demand | 核心摘要保留 + 详细迁出 |
| Knowledge Base Context        | Agent.md Knowledge Base          | Always-on | 保留       |
| Adapter Development Standards | `.agent/rules/adapter.md`      | On-demand | 迁出       |
| —                            | `.agent/rules/issue-driven.md` | On-demand | 新增                 |
| —                            | `.agent/solutions/`            | On-demand | 新增                 |

### 2.6 .gitignore 修改

**不修改**。`.agent/` 目录纳入版本控制，不需要添加到 .gitignore。

注意：`.trae/` 当前在 .gitignore 中，这是 Trae IDE 的运行时目录（含用户本地配置），与 `.agent/`（项目规则目录）性质不同。

## 3. 执行计划

| 步骤 | 内容                                  | 产出                                                   |
| ---- | ------------------------------------- | ------------------------------------------------------ |
| 1    | 创建 `.agent/` 目录结构             | 目录 + 空文件                                          |
| 2    | 编写 `.agent/rules/architecture.md` | 从 Agent.md 迁出术语 + 架构规范                        |
| 3    | 编写 `.agent/rules/adapter.md`      | 从 Agent.md 迁出 Adapter 规范                          |
| 4    | 编写 `.agent/rules/issue-driven.md` | 新增 Issue 驱动开发规则                                |
| 5    | 编写 `.agent/solutions/README.md`   | 索引文件                                               |
| 6    | 编写 3 个技术方案文件                 | git-branch-orphan / git-sandbox-write / gh-token-scope |
| 7    | 重构 Agent.md                         | 结构化入口 + 关键摘要 + 导航（≤ 250 行）              |
| 8    | 验证导航可达性                        | 从 Agent.md 出发，所有链接有效                         |
| 9    | 提交并创建 PR                         | PR                                                     |
