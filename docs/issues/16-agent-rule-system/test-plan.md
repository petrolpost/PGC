# Issue #16: 测试计划 — 规则系统重构

## 测试策略

本 Issue 是规则/文档层面的重构，不涉及代码逻辑，因此测试以**结构验证**和**内容完整性**为主，而非传统的单元测试。

测试分为 4 类：

- **S (Structure)**：文件/目录结构验证
- **C (Content)**：内容完整性验证
- **N (Navigation)**：导航可达性验证
- **M (Migration)**：迁移无遗漏验证

## 测试用例

### S-1: .agent/ 目录结构完整

**验证**：所有必需的目录和文件存在

```bash
ls -R .agent/
```

**期望输出包含**：

```
.agent/rules/architecture.md
.agent/rules/adapter.md
.agent/rules/issue-driven.md
.agent/solutions/README.md
.agent/solutions/git-branch-orphan.md
.agent/solutions/git-sandbox-write.md
.agent/solutions/gh-token-scope.md
```

### S-2: Agent.md 行数约束

**验证**：重构后 Agent.md 不超过 250 行

```bash
wc -l Agent.md
```

**期望**：≤ 250

### S-3: Agent.md 包含 Always-on / On-demand 分区标记

**验证**：Agent.md 中有明确的加载层级分区

```bash
grep -c "Always-on" Agent.md
grep -c "On-demand" Agent.md
```

**期望**：各出现 ≥ 1

### C-1: architecture.md 包含术语规范

**验证**：从 Agent.md 迁出的术语规范完整保留

```bash
grep -c "Persona" .agent/rules/architecture.md
grep -c "Governance Gate" .agent/rules/architecture.md
grep -c "CheckPoint" .agent/rules/architecture.md
```

**期望**：

- `Persona` 出现 ≥ 1
- `Governance Gate` 出现 ≥ 1
- `CheckPoint` 出现在禁止列表中 ≥ 1

### C-2: architecture.md 包含架构边界

**验证**：pgc_core / pgc_adapter 的边界定义完整

```bash
grep "pgc_core" .agent/rules/architecture.md
grep "pgc_adapter" .agent/rules/architecture.md
grep "NON-GOALS" .agent/rules/architecture.md
```

**期望**：三个关键词均存在

### C-3: adapter.md 包含完整 Adapter 规范

**验证**：Agent.md 原有的 5 个 Adapter 子章节全部迁出

```bash
for section in "Architecture" "Version Compatibility" "Version Upgrade Checklist" "Rendering Rules" "File Naming Convention"; do
  grep -c "$section" .agent/rules/adapter.md
done
```

**期望**：每个 section 出现 ≥ 1

### C-4: issue-driven.md 包含完整开发流程

**验证**：4 个 Phase 全部覆盖

```bash
for phase in "Issue 识别与提交" "Issue 认领与分支创建" "开发过程" "PR 提交与合并"; do
  grep -c "$phase" .agent/rules/issue-driven.md
done
```

**期望**：每个 Phase 出现 ≥ 1

### C-5: issue-driven.md 包含分支创建验证检查点

**验证**：包含孤立分支的预防措施

```bash
grep -c "git log" .agent/rules/issue-driven.md
grep -c "no commits yet" .agent/rules/issue-driven.md
grep -c "orphan" .agent/rules/issue-driven.md
```

**期望**：三个关键词均出现 ≥ 1

### C-6: 技术方案文件结构规范

**验证**：每个解决方案文件包含 4 个必需章节

```bash
for file in .agent/solutions/git-branch-orphan.md .agent/solutions/git-sandbox-write.md .agent/solutions/gh-token-scope.md; do
  for section in "Problem" "Root Cause" "Solution" "Verification"; do
    grep -c "$section" $file
  done
done
```

**期望**：每个文件的每个章节出现 ≥ 1

### C-7: solutions/README.md 索引完整

**验证**：索引包含所有 3 个方案文件

```bash
grep -c "git-branch-orphan" .agent/solutions/README.md
grep -c "git-sandbox-write" .agent/solutions/README.md
grep -c "gh-token-scope" .agent/solutions/README.md
```

**期望**：每个文件名出现 ≥ 1

### N-1: Agent.md 直接导航可达

**验证**：Agent.md 中引用的所有规则文件路径存在

```bash
for path in $(grep -oE '\.agent/[^ )"]+' Agent.md); do
  test -f "$path" && echo "OK: $path" || echo "MISSING: $path"
done
```

**期望**：所有路径输出 `OK`

### N-2: solutions/README.md 间接导航可达

**验证**：README.md 中引用的所有方案文件存在

```bash
for path in $(grep -oE '[a-z-]+\.md' .agent/solutions/README.md | grep -v README); do
  test -f ".agent/solutions/$path" && echo "OK: $path" || echo "MISSING: $path"
done
```

**期望**：所有路径输出 `OK`

### M-1: Agent.md 无冗余详细规范

**验证**：Agent.md 不再包含已迁出到 `.agent/rules/` 的详细规范（但保留摘要）

```bash
grep -c "BaseAdapter" Agent.md
grep -c "get_target_runtime_version" Agent.md
grep -c "render()" Agent.md
```

**期望**：全部为 0（这些详细规范已迁出到 adapter.md）

**注意**：术语摘要（如 Persona、Governance Gate）仍可在 Agent.md 中出现，因为 Agent.md 保留 Key Definitions 摘要

### M-2: 迁出内容无丢失

**验证**：原 Agent.md 中的关键概念在新文件中保留

原 Agent.md 关键概念清单：

- `Governance ≠ Control` → Agent.md Core Principles
- `Agent Autonomy First` → Agent.md Core Principles
- `Runtime Agnostic` → Agent.md Core Principles
- `Persona` (术语) → architecture.md
- `Governance Gate` (术语) → architecture.md
- `pgc_core` (边界) → architecture.md
- `pgc_adapter` (边界) → architecture.md
- `BaseAdapter` (Adapter 规范) → adapter.md
- `get_target_runtime_version` (版本兼容) → adapter.md
- `render()` (渲染规则) → adapter.md

```bash
for concept in "Governance ≠ Control" "Agent Autonomy First" "Runtime Agnostic" "Persona" "Governance Gate" "pgc_core" "pgc_adapter" "BaseAdapter" "get_target_runtime_version" "render()"; do
  found=$(grep -rl "$concept" Agent.md .agent/rules/ 2>/dev/null)
  if [ -n "$found" ]; then
    echo "OK: $concept → $found"
  else
    echo "LOST: $concept"
  fi
done
```

**期望**：所有概念均找到，无 `LOST`

## 测试执行顺序

```
S-1 → S-2 → S-3 → C-1 → C-2 → C-3 → C-4 → C-5 → C-6 → C-7 → N-1 → N-2 → M-1 → M-2
```

## DoD 验证清单

- [ ] S-1: .agent/ 目录结构完整
- [ ] S-2: Agent.md ≤ 250 行
- [ ] S-3: Agent.md 包含 Always-on / On-demand 分区标记
- [ ] C-1: architecture.md 包含术语规范
- [ ] C-2: architecture.md 包含架构边界
- [ ] C-3: adapter.md 包含完整 Adapter 规范
- [ ] C-4: issue-driven.md 包含 4 个 Phase
- [ ] C-5: issue-driven.md 包含分支创建验证检查点
- [ ] C-6: 技术方案文件结构规范
- [ ] C-7: solutions/README.md 索引完整
- [ ] N-1: Agent.md 直接导航可达
- [ ] N-2: solutions/README.md 间接导航可达
- [ ] M-1: Agent.md 无冗余详细规范
- [ ] M-2: 迁出内容无丢失
