# Issue #30: 测试计划 — 拆分 TGS Core 与 GitHub-backed Profile 边界

## 测试策略

本 Issue 是边界定义与文档收口类改动，验证重点不是业务逻辑输出，而是：

- **D (Documentation)**：关键文档是否完成边界收口
- **B (Boundary)**：是否明确区分 core / profile / adapter / package
- **R (Rendered Output)**：渲染得到的 `.tgs/instructions.md` 是否与新的边界文案一致
- **S (Scope)**：本次改动是否仍停留在 `#30` 范围内，没有提前侵入 `#31/#32/#33`

## 测试用例

### D-1: `tgs/README.md` 定义四层边界

**验证**：README 中存在 4 个层级术语

```bash
python -m pytest tests/test_tgs_docs.py -q
```

**期望**：

- `TGS Core`
- `TGS Profile`
- `TGS Adapter`
- `TGS Package`

均被文档检查覆盖。

### D-2: `tgs/operating-spec.md` 明确仓库级 profile 边界

**验证**：Operating Spec 中存在仓库分层说明

```bash
python -m pytest tests/test_tgs_docs.py -q
```

**期望**：

- 包含 `Layer Boundary In This Repo`
- 包含 `GitHub Object Mapping`
- 保留 `Old Rule Retirement Plan`

### D-3: `tgs/instructions.md` 只保留最小边界提示

**验证**：Instructions 文档说明自己不是 TGS Core 或 package format 定义位置

```bash
python -m pytest tests/test_tgs_docs.py -q
```

**期望**：

- 包含 `GitHub-backed TGS profile`
- 包含 `future TGS package format`

### R-1: `tgs:file` 渲染结果与源码文案一致

**验证**：assembler 渲染出的 `.tgs/instructions.md` 与新的边界措辞保持一致

```bash
python -m pytest tests/test_governance_config_assembler.py -q
```

**期望**：

- 渲染结果包含 `GitHub Issue-driven delivery is the default GitHub-backed TGS profile`
- 渲染结果包含 `future TGS package format`

### S-1: 本次变更未提前实现 profile 抽离

**验证**：本次改动只调整文档与渲染文案，不创建新的 `tgs/profiles/` 结构

```bash
git diff --name-only
```

**期望**：

- 不出现 `tgs/profiles/github-issue-driven/`

### S-2: 本次变更未提前实现 adapter 解耦或 package format

**验证**：本次改动不重构 assembler 注册机制，不新增 package manifest

```bash
git diff --name-only
```

**期望**：

- 不出现新的 package manifest 文件
- 不出现围绕 adapter registry 的结构性重构文件

## 建议执行顺序

```text
D-1 -> D-2 -> D-3 -> R-1 -> S-1 -> S-2
```

## DoD 验证清单

- [ ] D-1: `tgs/README.md` 定义四层边界
- [ ] D-2: `tgs/operating-spec.md` 明确仓库级 profile 边界
- [ ] D-3: `tgs/instructions.md` 只保留最小边界提示
- [ ] R-1: `tgs:file` 渲染结果与源码文案一致
- [ ] S-1: 本次变更未提前实现 profile 抽离
- [ ] S-2: 本次变更未提前实现 adapter 解耦或 package format
