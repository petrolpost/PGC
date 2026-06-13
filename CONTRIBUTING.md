# PGC Contributing Guide

欢迎参与 PGC (Persona-Governance-Capability) 项目的开发！
为了保证代码质量、架构一致性以及高效协作，本项目严格采用 **Issue-Driven Development (IDD, 议题驱动开发)** 模式。

无论你是人类贡献者，还是协助开发的 AI 助手，都必须遵循以下工作流。

---

## 🔄 核心工作流：Issue-Driven Development (IDD)

在 PGC 项目中，**没有 Issue，就没有代码变更**。所有的功能开发、Bug 修复和文档更新，都必须绑定到一个明确的 Issue。

### Step 1: 认领或创建 Issue

- 在开始任何工作前，检查 GitHub Issues 列表。
- 如果没有合适的 Issue，请先创建一个，明确描述：
  - **Context (背景)**：为什么要做这个？
  - **Tasks (任务)**：具体需要做什么？
  - **DoD (Definition of Done, 验收标准)**：如何证明这个 Issue 已经圆满完成？（必须是可验证的，如“通过 pytest”、“生成特定格式的 Markdown”）。

### Step 2: 分支开发 (Branching)

- 从 `main` 分支拉取新分支。
- 分支命名规范：`<type>/<issue-number>-<short-description>`
  - 示例：`feature/4-claude-adapter` 或 `fix/12-validator-type-error`

### Step 3: 编码与 AI 协作规范 (⚠️ 重要)

如果你使用 AI 助手协助开发，请在 Prompt 中**明确引用当前 Issue 的编号和 DoD**。

- ✅ **正确做法**：“请根据 Issue #4 的 DoD，实现 `ClaudeCodeAdapter`，确保输出的 `CLAUDE.md` 包含 `# Absolute Boundaries` 章节。”
- ❌ **错误做法**：“帮我写一个 Agent 适配器。”（过于模糊，容易导致架构漂移或过度设计）
- **AI 约束**：AI 生成的代码必须严格满足 Issue 的 DoD，不得擅自引入未讨论的第三方依赖或改变 Layer 0/1/2 的架构边界。

### Step 4: 提交与 Pull Request (PR)

- Commit 信息需遵循 Conventional Commits 规范，并关联 Issue：
  - 示例：`feat(adapter): implement ClaudeCodeAdapter (#4)`
- 提交 PR 时，必须在描述中写明：
  - 关联的 Issue 编号（如 `Closes #4`）。
  - 如何验证 DoD 已被满足（例如提供测试命令或输出截图）。

### Step 5: 验收与关闭 (Review & Close)

- Maintainer 将根据 Issue 中的 **DoD** 逐条核对 PR。
- 只有当所有 DoD 均被满足，且通过 CI/CD 检查后，PR 才会被合并，Issue 自动关闭。

---

## 🏗️ 架构红线 (Architecture Red Lines)

在提交任何代码前，请确保你的修改没有违反 PGC 的核心哲学：

1. **Layer 0 (`pgc_core`) 必须保持纯净**：严禁引入任何 Runtime、Workflow 或 LLM 相关的依赖。
2. **术语一致性**：严禁使用 `CheckPoint`, `Skill`, `Hook`。必须使用 `Governance Gate`, `Capability`, `Governance Binding`。
3. **声明优于实现**：PGC 只定义“是什么 (What)”，不规定“怎么做 (How)”。

---

## 🚀 快速开始

1. Fork 本仓库并 Clone 到本地。
2. 安装开发依赖：`pip install -e ".[dev]"` (包含 `pytest`, `typer`, `pydantic`, `pyyaml`)。
3. 运行测试确保环境正常：`pytest`。
4. 前往 [Issues](../../issues) 挑选你的第一个任务！
