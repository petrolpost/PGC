# Issue #13: 测试计划

## 1. 测试范围

| 模块 | 文件 | 测试类型 | 用例数 |
|------|------|----------|--------|
| TraeAdapter | test_trae_adapter.py | 单元 | 12 |
| TraeAdapter Versioning | test_trae_adapter.py | 单元 | 5 |
| **合计** | | | **17** |

## 2. 测试用例

### 2.1 test_trae_adapter.py

| 用例 ID | 描述 | 输入/操作 | 预期结果 | 验证点 |
|---------|------|-----------|----------|--------|
| TR-1 | 继承 BaseAdapter | `isinstance(adapter, BaseAdapter)` | True | 继承关系 |
| TR-2 | get_target_runtime | 调用方法 | `"trae"` | 运行时标识 |
| TR-3 | get_target_runtime_version | 调用方法 | `"trae@1.3"` | 运行时版本 |
| TR-4 | get_supported_extensions | 调用方法 | `[".md"]` | 扩展名 |
| TR-5 | render 返回正确文件路径 | 合规文档 | key 以 `.trae/rules/` 开头 | 路径格式 |
| TR-6 | Persona 生成独立文件 | 单 Persona 文档 | 包含 `.trae/rules/persona-{id}.md` | 文件拆分 |
| TR-7 | Persona 文件包含 frontmatter | 单 Persona 文档 | 包含 `alwaysApply: true` 和 `---` | frontmatter 格式 |
| TR-8 | Persona 文件包含职责 | 单 Persona 文档 | 包含 `## Responsibilities` 和职责内容 | 章节内容 |
| TR-9 | Boundaries 文件 | 含 boundaries 的文档 | 包含 `.trae/rules/boundaries.md`，含 `NEVER:` | 章节内容 |
| TR-10 | Governance 文件 | 含 binding 的文档 | 包含 `.trae/rules/governance.md`，含 gate 描述和 authority level | 章节内容 |
| TR-11 | Capabilities 文件智能生效 | 含 capability 的文档 | 包含 `alwaysApply: false` 和 `description:` | frontmatter 字段 |
| TR-12 | 空 boundaries 不生成文件 | 无 boundaries 的文档 | 不包含 `.trae/rules/boundaries.md` key | 空章节省略 |

## 3. 测试数据

### 3.1 Fixture

复用 `tests/conftest.py` 中的 `make_valid_doc()` 和 `make_multi_doc()`。

### 3.2 额外边界数据

| 场景 | 构造方式 | 用途 |
|------|----------|------|
| 无 boundaries 的 Persona | `negative_boundaries=[]` | TR-12: 不生成空 boundaries 文件 |
| 无 capabilities 的文档 | `capabilities=[]` | TR-11: 不生成空 capabilities 文件 |
| 多 Persona | `make_multi_doc()` | TR-6: 多个 persona 文件 |
| WARN 级别 binding | `authority_level="advisory"` | TR-10: 非 STRICT 不含 STOP 提示 |

### 3.3 预期输出片段

测试通过 `in` 断言检查关键片段，而非完整字符串匹配，避免模板微调导致测试脆弱。

关键断言示例：
```python
output = adapter.render(doc)

# 路径格式
assert ".trae/rules/persona-frontend.md" in output

# frontmatter
content = output[".trae/rules/persona-frontend.md"]
assert "alwaysApply: true" in content
assert "---" in content

# 内容
assert "## Responsibilities" in content
assert "NEVER:" in output[".trae/rules/boundaries.md"]
assert "# Governance Rules" in output[".trae/rules/governance.md"]

# Capabilities 智能生效
assert "alwaysApply: false" in output[".trae/rules/capabilities.md"]
assert "description:" in output[".trae/rules/capabilities.md"]
```

版本兼容性断言示例：
```python
from pgc_core.validator import check_runtime_compatibility

adapter = TraeAdapter()

# TR-V1: 兼容
warnings = check_runtime_compatibility(doc_with_trae_runtime, adapter.get_target_runtime_version())
assert len(warnings) == 0

# TR-V2: 版本过高
warnings = check_runtime_compatibility(doc_with_high_trae_runtime, adapter.get_target_runtime_version())
assert len(warnings) > 0
assert "incompatibility" in warnings[0].lower() or "Version" in warnings[0]

# TR-V3: 运行时名称不匹配
warnings = check_runtime_compatibility(doc_with_wrong_runtime, adapter.get_target_runtime_version())
assert len(warnings) > 0
assert "mismatch" in warnings[0].lower()

# TR-V4 / TR-V5: 向后兼容
warnings = check_runtime_compatibility(doc_no_metadata, adapter.get_target_runtime_version())
assert len(warnings) == 0
```

## 4. 测试策略

- **运行方式**: `pytest tests/test_trae_adapter.py -v`
- **断言风格**: 子字符串包含断言（`in`），不依赖精确格式
- **隔离性**: 每个测试独立构造 PGCDocument
- **覆盖率**: 目标 >= 90% for `pgc_adapter/trae/generator.py`
