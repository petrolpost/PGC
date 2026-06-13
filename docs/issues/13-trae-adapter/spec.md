# Issue #13: 实现 TraeAdapter (生成 .trae/rules/ 规则文件)

## 1. 需求分析

### 1.1 背景

PGC 的核心价值链是：**PGCDocument (YAML) → Adapter → Runtime 配置文件**。ClaudeCodeAdapter 已完成，将 PGC 编译为 `CLAUDE.md`。TraeAdapter 是第二个 Adapter 实现，将 PGC 治理契约翻译为 Trae IDE 原生的 `.trae/rules/` 规则文件体系。

### 1.2 Trae IDE 规则机制概要

Trae IDE 使用 Markdown 规则文件 + YAML frontmatter 控制生效方式：

- **文件位置**：`.trae/rules/<rule-name>.md`（项目级），支持最多 3 层子目录嵌套
- **frontmatter 字段**：
  - `alwaysApply: true/false` — 是否始终生效
  - `description: "..."` — 智能生效时的适用场景描述
  - `globs: "*.js, src/**/*.ts"` — 指定文件生效时的 glob 匹配模式
  - `scene: git_message` — 专用于 Git 提交信息生成
- **生效方式**：始终生效 / 指定文件生效 / 智能生效 / 手动触发
- **兼容性**：Trae 也支持读取 `AGENTS.md` 和 `CLAUDE.md`，但原生规则文件提供更精细的生效控制

> **版本注意**：`.rules` frontmatter 机制（`alwaysApply`、`description`、`globs`）从 Trae IDE **v1.3.0** 起引入。v1.3.0 之前的版本仅支持 `project_rules.md` / `user_rules.md` 纯 Markdown 格式，不支持 frontmatter 和多文件拆分。本 Adapter 生成的内容需要 Trae >= 1.3.0 才能正确生效。

### 1.3 目标

1. 继承 `BaseAdapter`，实现 `TraeAdapter`
2. 将 `Persona` 映射为 `.trae/rules/persona-{id}.md`（`alwaysApply: true`）
3. 将 `GovernanceGate` + `GovernanceBinding` 映射为 `.trae/rules/governance.md`（`alwaysApply: true`）
4. 将 `Persona.negative_boundaries` 映射为 `.trae/rules/boundaries.md`（`alwaysApply: true`）
5. 将 `Capability` 映射为 `.trae/rules/capabilities.md`（智能生效，`description` 标注适用场景）

### 1.4 约束

- 输入必须是已通过验证的 `PGCDocument`
- 输出为 `Dict[str, str]`，key 为相对路径（如 `.trae/rules/persona-frontend.md`），value 为带 frontmatter 的 Markdown 内容
- 不做 IO 写入，只返回字符串映射
- 必须通过 `BaseAdapter` 的 `validate_compatibility()` 检查
- frontmatter 使用 `---` 分隔，格式遵循 Trae 官方规范

### 1.5 版本兼容性策略

遵循 Issue #11 建立的 Adapter 运行时版本化机制：

- **Adapter 声明版本**：`TraeAdapter.get_target_runtime_version()` 返回 `"trae@1.3"`，表示支持 Trae IDE v1.3.0+ 的 `.rules` frontmatter 机制
- **文档声明版本**：PGCDocument 可通过 `metadata.target_runtime` 声明目标运行时，如 `trae@>=1.3`
- **兼容性检查**：`check_runtime_compatibility()` 在 `pgc validate` 时自动校验文档与 Adapter 的版本匹配
- **版本匹配规则**：
  - 文档声明 `trae@>=1.3`，Adapter 支持 `trae@1.3` → 兼容
  - 文档声明 `trae@>=2.0`，Adapter 支持 `trae@1.3` → 不兼容（警告）
  - 文档声明 `claude-code@>=1.0`，Adapter 是 `trae@1.3` → 运行时名称不匹配（警告）
  - 文档未声明 `target_runtime` → 跳过检查（向后兼容）
- **版本升级路径**：当 Trae IDE 后续版本引入新的规则字段（如 v1.4.0 的 UI 配置），只需更新 `get_target_runtime_version()` 返回值并在 render 中适配新字段，旧版本文档通过 SemVer 比较自动获得兼容性警告

## 2. 设计方案

### 2.1 映射规则

| PGC 实体 | 输出文件 | frontmatter | 映射逻辑 |
|----------|----------|-------------|----------|
| `Persona` | `.trae/rules/persona-{id}.md` | `alwaysApply: true` | 每个 Persona 生成独立文件，包含角色职责描述 |
| `Persona.negative_boundaries` | `.trae/rules/boundaries.md` | `alwaysApply: true` | 所有 Persona 的边界合并为一个文件，使用 `NEVER:` 语法 |
| `GovernanceGate` + `GovernanceBinding` | `.trae/rules/governance.md` | `alwaysApply: true` | 所有治理规则合并为一个文件，包含 gate 描述、authority level 和 violation policy |
| `Capability` | `.trae/rules/capabilities.md` | `alwaysApply: false`, `description: "When using or invoking capabilities"` | 能力声明文件，智能生效 |

### 2.2 规则文件模板

#### persona-{id}.md

```markdown
---
alwaysApply: true
---

# {persona.name} (`{persona.id}`)

## Responsibilities

- {responsibility_1}
- {responsibility_2}

## Output Target

{persona.output_target}
```

#### boundaries.md

```markdown
---
alwaysApply: true
---

# Absolute Boundaries

> **NEVER** violate these boundaries under any circumstances.

- **[{persona.name}]** NEVER: {boundary_1}
- **[{persona.name}]** NEVER: {boundary_2}
```

#### governance.md

```markdown
---
alwaysApply: true
---

# Governance Rules

| Rule | Gate | Authority | On Violation |
|------|------|-----------|--------------|
| {gate.description} | `{gate.id}` | {authority_level} | {violation_policy} |

> When a STRICT rule is violated: **STOP and ask for human review.**
```

#### capabilities.md

```markdown
---
alwaysApply: false
description: "When using or invoking capabilities defined in the PGC governance contract"
---

# Capabilities

| Capability | Owner | Description |
|-----------|-------|-------------|
| `{cap.id}` | {cap.owner_persona} | {cap.description} |
```

### 2.3 类设计

```python
class TraeAdapter(BaseAdapter):
    """Translates PGCDocument into Trae IDE's .trae/rules/ format."""

    RULES_DIR = ".trae/rules"

    def render(self, document: PGCDocument) -> Dict[str, str]:
        """Render PGCDocument to .trae/rules/ files."""
        output: Dict[str, str] = {}

        # Persona files
        for persona in document.personas:
            path = f"{self.RULES_DIR}/persona-{persona.id}.md"
            output[path] = self._render_persona(persona)

        # Boundaries file
        boundaries = self._render_boundaries(document.personas)
        if boundaries:
            output[f"{self.RULES_DIR}/boundaries.md"] = boundaries

        # Governance file
        output[f"{self.RULES_DIR}/governance.md"] = self._render_governance(document)

        # Capabilities file
        capabilities = self._render_capabilities(document.capabilities)
        if capabilities:
            output[f"{self.RULES_DIR}/capabilities.md"] = capabilities

        return output

    def get_target_runtime(self) -> str:
        return "trae"

    def get_target_runtime_version(self) -> str:
        return "trae@1.3"

    def get_supported_extensions(self) -> List[str]:
        return [".md"]

    # Private rendering methods
    def _render_persona(self, persona: Persona) -> str: ...
    def _render_boundaries(self, personas: List[Persona]) -> str: ...
    def _render_governance(self, document: PGCDocument) -> str: ...
    def _render_capabilities(self, capabilities: List[Capability]) -> str: ...
```

### 2.4 文件结构

```
pgc_adapter/
  __init__.py              # 已有，添加 TraeAdapter 导出
  base.py                  # 已有
  claude/
    ...                    # 已有
  trae/
    __init__.py            # 导出 TraeAdapter
    generator.py           # TraeAdapter 实现
```

### 2.5 设计决策

| 决策 | 选项 | 选择 | 理由 |
|------|------|------|------|
| Persona 是否拆分为独立文件 | 是 / 否 | 是 | Trae 支持子目录嵌套和独立规则文件，拆分后可单独引用，更灵活 |
| Boundaries 是否独立文件 | 合并到 persona / 独立 | 独立 | 边界是全局约束，应始终生效且集中管理 |
| Capabilities 的生效方式 | 始终生效 / 智能生效 | 智能生效 | 能力声明仅在相关场景需要，避免无关上下文噪音 |
| Governance 的生效方式 | 始终生效 / 智能生效 | 始终生效 | 治理规则是核心约束，必须在所有对话中生效 |
| 空 boundaries/capabilities 是否生成文件 | 是 / 否 | 否 | 避免空文件，减少噪音 |
| 是否生成 AGENTS.md | 是 / 否 | 否 | Trae 原生 .trae/rules/ 提供更精细控制，无需降级到 AGENTS.md |

## 3. 执行计划

| 步骤 | 内容 | 产出 |
|------|------|------|
| 1 | 实现 `TraeAdapter` | `pgc_adapter/trae/generator.py` |
| 2 | 创建 `pgc_adapter/trae/__init__.py` | 导出 |
| 3 | 更新 `pgc_adapter/__init__.py` | 导出 TraeAdapter |
| 4 | 编写测试 | `tests/test_trae_adapter.py` |
| 5 | 运行 pytest | 确认通过 |
| 6 | 提交并创建 PR | PR |
