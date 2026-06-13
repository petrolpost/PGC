# Issue #3: 测试计划

## 1. 测试范围

| 模块 | 文件 | 测试类型 | 用例数 |
|------|------|----------|--------|
| BaseAdapter 抽象约束 | test_base_adapter.py | 单元 | 6 |
| **合计** | | | **6** |

## 2. 测试用例

### 2.1 test_base_adapter.py

| 用例 ID | 描述 | 输入/操作 | 预期结果 | 验证点 |
|---------|------|-----------|----------|--------|
| BA-1 | 不能直接实例化 BaseAdapter | `BaseAdapter()` | `TypeError` | ABC 约束生效 |
| BA-2 | 不实现全部抽象方法的子类不能实例化 | 只实现 `render` 的子类 | `TypeError` | 缺少方法被拦截 |
| BA-3 | 实现全部抽象方法的子类可以实例化 | 完整子类 | 实例化成功 | ABC 契约完整 |
| BA-4 | render 返回正确类型 | 调用 `render(doc)` | `Dict[str, str]` | 返回值类型和内容 |
| BA-5 | get_target_runtime / get_supported_extensions 返回正确值 | 调用元数据方法 | str / List[str] | 返回值类型 |
| BA-6 | validate_compatibility 默认行为 | 空 doc / 有内容的 doc | False / True | 默认实现逻辑 |

## 3. 测试数据

### 3.1 测试用 Stub Adapter

在测试文件中定义一个 `StubAdapter`，实现全部抽象方法，用于测试 BaseAdapter 的行为约束：

```python
class StubAdapter(BaseAdapter):
    def render(self, document: PGCDocument) -> Dict[str, str]:
        return {"stub.txt": f"personas: {len(document.personas)}"}

    def get_target_runtime(self) -> str:
        return "stub-runtime"

    def get_supported_extensions(self) -> List[str]:
        return [".txt"]
```

### 3.2 PGCDocument fixture

复用 `tests/conftest.py` 中的 `make_valid_doc()` 和 `make_multi_doc()` 生成测试文档。

### 3.3 边界数据

| 场景 | 构造方式 | 用途 |
|------|----------|------|
| 空文档 | `PGCDocument(personas=[], governance_gates=[], capabilities=[], governance_bindings=[])` | BA-6: validate_compatibility 返回 False |
| 最小合规 | `make_valid_doc()` | BA-4, BA-5, BA-6: 正常路径 |
| 多实体 | `make_multi_doc()` | BA-4: render 内容验证 |

## 4. 测试策略

- **运行方式**: `pytest tests/test_base_adapter.py -v`
- **类型检查**: `mypy pgc_adapter/base.py --strict`（需先安装 mypy）
- **断言风格**: `pytest.raises(TypeError)` + 直接断言返回值
- **隔离性**: StubAdapter 在测试文件内定义，不污染生产代码
