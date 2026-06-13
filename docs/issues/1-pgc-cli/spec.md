# Issue #1: [Core] 完善 pgc-core CLI 工具 (pgc init & pgc validate)

**GitHub Issue**: https://github.com/petrolpost/PGC/issues/1
**Milestone**: Phase 1: Core Foundation
**Labels**: layer-0, enhancement, good first issue

---

## 1. 需求分析

### 背景

`pgc_core` 已具备基础的验证能力（`PGCValidator` + `PGCDocument` 模型），但缺乏便捷的脚手架和目录级批量验证的 CLI 封装。用户需要开箱即用的命令行体验。

### 核心需求

| ID | 需求 | 来源 |
|----|------|------|
| R-1 | 使用 `typer` 完善 CLI 入口 | Issue Tasks |
| R-2 | `pgc validate <path>`：支持单文件和目录递归验证，输出美观终端报告 | Issue Tasks |
| R-3 | `pgc init <dir>`：生成标准 `agent.pgc.yaml` 模板和 `.pgc/` 目录结构 | Issue Tasks |

### 约束

- Layer 0 (`pgc_core`) 保持纯净，不引入 Runtime/Workflow/LLM 依赖
- CLI 依赖（`typer`, `rich`）属于用户交互层，不污染核心模型
- 术语遵循 PGC 规范：`Persona`, `Governance Gate`, `Capability`, `Governance Binding`

---

## 2. 设计方案

### 模块划分

```
pgc_core/
  cli.py          # CLI 入口 (typer app + init/validate 命令)
  model.py        # PGCDocument 模型 (已有，不改动)
  validator.py    # PGCValidator 验证引擎 (已有，修复 import)
```

### 接口定义

#### `pgc init <dir>`

```
输入: 目标目录路径 (必须不存在或为空)
输出:
  - <dir>/agent.pgc.yaml   # 标准 PGC 模板
  - <dir>/.pgc/README.md   # 运行时产物目录说明
副作用: 创建目录结构
退出码: 0=成功, 1=目录已存在且非空
```

#### `pgc validate <path>`

```
输入: YAML 文件路径 或 目录路径
行为:
  - 文件: 验证单个 .pgc.yaml
  - 目录: 递归扫描所有 *.pgc.yaml 文件
输出: Rich Table 格式的验证报告
  - [OK] Success (绿色)
  - [FAIL] Failed (红色) + 错误详情
退出码: 0=全部通过, 1=存在验证错误或路径不存在
```

### 模板设计

`agent.pgc.yaml` 模板包含 PGC 规范 v0.3 的全部五个顶层 key：
- `personas` / `governance_gates` / `capabilities` / `governance_bindings` / `governance_authority`

模板内容必须自身通过 `pgc validate` 验证（自举性）。

### 依赖关系

```
cli.py → validator.py → model.py
                       → pyyaml
         typer, rich
```

---

## 3. 执行计划

| 步骤 | 内容 | 产出 |
|------|------|------|
| E-1 | 创建 `pyproject.toml`（项目配置 + CLI 入口点） | pyproject.toml |
| E-2 | 修复 `validator.py` 的 import 错误 (`from .models` → `from .model`) | validator.py |
| E-3 | 实现 `cli.py`：`pgc init` + `pgc validate` | cli.py |
| E-4 | Windows 兼容性修复（GBK 编码问题，避免 emoji） | cli.py |
| E-5 | 编写测试代码 | tests/test_cli.py |
| E-6 | DoD 验证 | 手动 + pytest |
