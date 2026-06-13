# Issue #11: Adapter 运行时版本化机制 — Spec

## 1. 需求分析

### 背景

Agent 运行时（Claude Code、Cursor 等）在快速迭代，PGC 的映射关系需要版本化：
- 不同版本的运行时使用对应的适配策略
- 运行时升级后可平滑过渡，旧版本标记为 deprecated
- 验证时检查 PGC 文档与目标运行时的兼容性

### 核心需求

1. **BaseAdapter 版本方法**：每个 Adapter 声明支持的目标运行时版本
2. **PGCDocument 元数据**：文档声明目标运行时及版本范围
3. **版本兼容性检查**：`pgc validate` 校验文档声明的运行时版本是否在 Adapter 支持范围内
4. **映射文档版本标注**：文档头部标注适用的运行时版本范围和状态

### 约束

- 版本格式遵循 `runtime@version` 规范（如 `claude-code@1.0`）
- 版本比较使用语义化版本（SemVer）
- 向后兼容：无 `metadata` 字段的旧文档仍可正常验证
- 不引入额外依赖，使用 `packaging.version`（Python 标准库已有或轻量依赖）

## 2. 设计方案

### 2.1 模块变更

```
pgc_core/
  model.py        # 新增 PGCMetadata + PGCDocument.metadata 字段
  validator.py    # 新增版本兼容性检查逻辑
  cli.py          # init 模板增加 metadata 段，validate 增加版本警告
pgc_adapter/
  base.py         # BaseAdapter 新增 get_target_runtime_version()
  claude/
    generator.py  # ClaudeCodeAdapter 实现 get_target_runtime_version()
docs/runtime-mapping/
  claude-code.md  # 头部增加版本元信息 YAML front matter
```

### 2.2 接口定义

#### PGCMetadata 模型

```python
class PGCMetadata(BaseModel):
    target_runtime: Optional[str] = Field(
        default=None,
        description="Target runtime with version, e.g. 'claude-code@>=1.0'"
    )
    model_config = ConfigDict(extra="forbid")
```

#### PGCDocument 变更

```python
class PGCDocument(BaseModel):
    metadata: Optional[PGCMetadata] = Field(default=None)
    # ... 其余字段不变
```

#### BaseAdapter 新增方法

```python
@abstractmethod
def get_target_runtime_version(self) -> str:
    """Return supported runtime version, e.g. 'claude-code@1.0'."""
    ...
```

#### 版本兼容性检查

```python
def check_runtime_compatibility(document: PGCDocument, adapter: BaseAdapter) -> List[str]:
    """Check if document's target_runtime is compatible with adapter.
    Returns list of warning messages (empty = compatible)."""
```

### 2.3 版本匹配规则

- 文档声明 `claude-code@>=1.0`，Adapter 支持 `claude-code@1.0` → 兼容
- 文档声明 `claude-code@>=2.0`，Adapter 支持 `claude-code@1.0` → 不兼容（警告）
- 文档未声明 `target_runtime` → 跳过检查（向后兼容）
- 文档声明的运行时名称与 Adapter 不匹配 → 警告

### 2.4 依赖

- `packaging>=21.0`：用于 SemVer 版本比较（已是 Python 生态标准）

## 3. 执行计划

| Step | 内容 | 依赖 |
|------|------|------|
| 1 | `model.py` 新增 `PGCMetadata`，`PGCDocument` 增加 `metadata` 字段 | 无 |
| 2 | `base.py` 新增 `get_target_runtime_version()` 抽象方法 | Step 1 |
| 3 | `ClaudeCodeAdapter` 实现 `get_target_runtime_version()` | Step 2 |
| 4 | `validator.py` 新增 `check_runtime_compatibility()` | Step 1, 2 |
| 5 | `cli.py` init 模板增加 metadata 段 | Step 1 |
| 6 | `cli.py` validate 增加版本兼容性警告输出 | Step 4 |
| 7 | 映射文档增加版本 front matter | 无 |
| 8 | 编写测试 | Step 1-6 |
| 9 | `pyproject.toml` 增加 `packaging` 依赖 | Step 4 |
