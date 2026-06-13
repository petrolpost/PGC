# Issue #4: 测试计划

## 1. 测试范围

| 模块 | 文件 | 测试类型 | 用例数 |
|------|------|----------|--------|
| ClaudeCodeAdapter | test_claude_adapter.py | 单元 | 10 |
| **合计** | | | **10** |

## 2. 测试用例

### 2.1 test_claude_adapter.py

| 用例 ID | 描述 | 输入/操作 | 预期结果 | 验证点 |
|---------|------|-----------|----------|--------|
| CC-1 | 继承 BaseAdapter | `isinstance(adapter, BaseAdapter)` | True | 继承关系 |
| CC-2 | get_target_runtime | 调用方法 | `"claude-code"` | 运行时标识 |
| CC-3 | get_supported_extensions | 调用方法 | `[".md"]` | 扩展名 |
| CC-4 | render 返回 CLAUDE.md | 合规文档 | `{"CLAUDE.md": "..."}` | key 存在且为 str |
| CC-5 | Persona 映射到 Role & Responsibilities | 单 Persona 文档 | 包含 `## Code Reviewer` 和 responsibilities | 章节内容 |
| CC-6 | negative_boundaries 映射到 Absolute Boundaries | 含 boundaries 的文档 | 包含 `NEVER:` 和 boundary 内容 | 章节内容 |
| CC-7 | Governance 映射到 Governance Rules | 含 binding 的文档 | 包含 gate 描述和 authority level | 章节内容 |
| CC-8 | STRICT 违规提示 | authority=STRICT | 包含 "STOP and ask for human review" | 违规行为提示 |
| CC-9 | Output Targets 章节 | 含 output_target 的文档 | 包含 persona 和 target 的映射表 | 章节内容 |
| CC-10 | Capabilities 章节 | 含 capability 的文档 | 包含 capability id、owner、description | 章节内容 |

## 3. 测试数据

### 3.1 Fixture

复用 `tests/conftest.py` 中的 `make_valid_doc()` 和 `make_multi_doc()`。

### 3.2 额外边界数据

| 场景 | 构造方式 | 用途 |
|------|----------|------|
| 无 boundaries 的 Persona | `negative_boundaries=[]` | CC-6: 不渲染空章节 |
| 多 Persona | `make_multi_doc()` | CC-5: 多角色渲染 |
| WARN 级别 binding | `authority_level="advisory"` | CC-8: 非 STRICT 不含 STOP |

### 3.3 预期输出片段

测试通过 `in` 断言检查关键片段，而非完整字符串匹配，避免模板微调导致测试脆弱。

关键断言示例：
```python
output = adapter.render(doc)["CLAUDE.md"]
assert "# Role & Responsibilities" in output
assert "## Code Reviewer" in output
assert "NEVER:" in output
assert "# Governance Rules" in output
```

## 4. 测试策略

- **运行方式**: `pytest tests/test_claude_adapter.py -v`
- **断言风格**: 子字符串包含断言（`in`），不依赖精确格式
- **隔离性**: 每个测试独立构造 PGCDocument
- **覆盖率**: 目标 >= 90% for `pgc_adapter/claude/generator.py`
