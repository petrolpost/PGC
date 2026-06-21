# Issue #30: 拆分 TGS Core 与 GitHub-backed Profile 边界

## 1. 需求分析

### 1.1 背景

当前仓库已经把 GitHub Issue-driven workflow 收编为本项目的第一版 TGS 落地方式，并新增了 [TGS Operating Spec](file:///e:/workspaces/self/PGC/tgs/operating-spec.md)。但从概念和模块边界看，仓库里仍然混合着 4 层不同性质的内容：

1. **TGS Core**：通用的追溯概念、契约和完整性等级
2. **GitHub-backed TGS**：把 GitHub Issue / PR / review / merge 等对象映射为 TGS 语义的仓库级运行配置
3. **TGS Adapter**：把 TGS 内容渲染到工作区运行文件的装配逻辑
4. **TGS Package**：未来如果要把 GitHub-backed TGS 做成可挂载配件，需要额外定义的分发/安装层

如果在这 4 层没有明确边界的情况下继续演进：

- `GitHub-backed TGS` 容易被误解成 TGS 本体
- `tgs/` 和 `.tgs/` 的语义会继续混淆
- 后续 `#31` 的 profile 抽离、`#32` 的 assembler 解耦、`#33` 的 package format 设计都会互相污染

### 1.2 目标

1. 正式定义 `TGS Core`、`TGS Profile`、`TGS Adapter`、`TGS Package` 四层职责
2. 收紧 `GitHub-backed TGS` 的定位：它是 **Profile**，不是 TGS 本体
3. 明确 `tgs/` 与 `.tgs/` 的职责差异
4. 维持当前阶段继续沿用 `Issue Driven` 作为变更追踪与交付纪律
5. 为后续 `#31`、`#32`、`#33` 提供稳定边界

### 1.3 约束

- **不越权到后续 Issue**：本次只拆边界，不提前做 profile 抽离、adapter 重构或 package format 设计
- **保留当前工作流**：本次不替换 `Issue Driven`，只说明它与 TGS 的关系
- **Git 跟踪**：文档必须落在仓库内可跟踪路径，而不是仅保留在 `.trae/`
- **术语一致**：统一使用 `TGS Core`、`TGS Profile`、`TGS Adapter`、`TGS Package`
- **最小改动原则**：先收口表述边界，再进入后续实现类改动

## 2. 设计方案

### 2.1 四层职责边界

| 层级 | 职责 | 应包含 | 不应包含 |
|------|------|--------|----------|
| **TGS Core** | 定义通用追溯概念和契约 | Anchor / Action / Artifact / Verification、integrity levels、通用 contract | GitHub Issue/PR 这类平台特定对象 |
| **TGS Profile** | 定义某一平台如何承载 TGS | GitHub-backed 映射、仓库级运行解释、phase mapping | 通用契约定义本身、分发包格式 |
| **TGS Adapter** | 将 TGS 内容渲染为运行文件 | `.tgs/instructions.md`、`.tgs/audit-report.md` 等输出逻辑 | Profile 的业务语义定义本身 |
| **TGS Package** | 定义未来的可分发配件格式 | manifest、安装流程、升级与验证边界 | 当前仓库运行中的临时产物目录 |

### 2.2 GitHub-backed TGS 的定位

本仓库中的 `GitHub-backed TGS` 应被定义为：

- 基于 `TGS Core` 的一个 **repository-local operating profile**
- 当前 PGC 项目所采用的第一版 TGS 落地方式
- 通过 GitHub Issue、spec、PR、review、merge、close 等对象承载 TGS 语义

它**不是**：

- TGS 本体
- TGS 的全部能力边界
- 已经独立完成配件化分发的 package

### 2.3 `tgs/` 与 `.tgs/` 的职责差异

| 位置 | 角色 | 说明 |
|------|------|------|
| `tgs/` | source-of-truth | 存放 TGS 的规范、模板、适配文档和运行说明 |
| `.tgs/` | rendered runtime outputs | 存放安装或渲染后生成的工作区运行产物 |

设计结论：

- `tgs/` 属于源码/规范层
- `.tgs/` 属于运行产物层
- 将来如果设计正式分发包，分发包不应直接等同于 `.tgs/`

### 2.4 与 Issue Driven 的关系

当前阶段继续沿用 `Issue Driven`，其职责是：

- 变更入口
- 认领与分支纪律
- spec-first 与 PR/close 规则

TGS 在当前阶段负责的是：

- 解释同一条变更链为什么是可追溯的
- 将 GitHub 对象映射为 TGS 语义
- 为后续 profile 抽离和配件化奠定边界

因此本次变更的策略是：

- **保留 Issue Driven**
- **收紧 TGS 边界**
- **不提前做后续实现**

### 2.5 与后续 Issue 的依赖关系

| Issue | 主题 | 依赖本 Issue 的原因 |
|------|------|------------------|
| `#31` | 抽离 GitHub issue-driven profile | 必须先明确 `GitHub-backed TGS` 是 profile |
| `#32` | 去除 assembler 对 TGS 的硬编码路径 | 必须先明确 adapter 层与 profile 层的边界 |
| `#33` | 定义 package format 与 install flow | 必须先明确 `tgs/` 与 `.tgs/` 的职责差异 |

## 3. 执行计划

| 步骤 | 内容 | 产出 |
|------|------|------|
| 1 | 盘点现有文档中的边界混杂点 | 差异清单 |
| 2 | 定义四层术语与职责 | 边界定义 |
| 3 | 收紧 GitHub-backed TGS 的仓库级表述 | 文档修订方案 |
| 4 | 明确 `tgs/` 与 `.tgs/` 的目录语义 | 目录边界说明 |
| 5 | 对齐仓库文档入口 | `tgs/README.md`、`tgs/operating-spec.md`、必要的 handoff 文案 |
| 6 | 验证本次变更未越权到 `#31/#32/#33` | 范围边界检查 |
