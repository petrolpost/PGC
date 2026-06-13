# Issue #2: 补充核心模型与验证规则的单元测试

## 1. 需求分析

### 1.1 背景

`pgc_core/model.py` 中的 `PGCDocument` 通过 `@model_validator` 实现了三条核心治理规则：

| 规则 | 名称 | 触发时机 | 预期行为 |
|------|------|----------|----------|
| R1 | Referential Integrity | Binding 引用不存在的 ID | `ValueError` |
| R2 | Capability Ownership | Capability 归属与 Binding 分配不一致 | `ValueError` |
| R3 | Gate Coverage | Gate 未被任何 Binding 绑定 | `ValueError` |

当前 `tests/test_models.py` 和 `tests/test_validator.py` 均为空文件，这三条规则完全没有测试覆盖。同时 `pgc_core/validator.py` 的 `PGCValidator` 类（`load_and_validate` / `validate_directory`）也缺乏测试。

### 1.2 目标

1. 为 `PGCDocument` 的 `@model_validator` 编写单元测试，覆盖所有验证规则的正常路径和异常路径
2. 为 `PGCValidator` 编写集成测试，覆盖文件加载、YAML 解析、验证错误格式化等场景
3. 测试覆盖率达到 **90%** 以上

### 1.3 约束

- 不修改 `model.py` 和 `validator.py` 的实现代码
- 测试文件遵循 Issue 描述中的 4 文件划分
- 测试数据通过 helper 函数动态生成，不依赖外部 fixture 文件

## 2. 设计方案

### 2.1 测试文件划分

```
tests/
  test_valid_document.py          # 完整合规文档加载
  test_referential_integrity.py   # 引用完整性 (R1)
  test_capability_ownership.py    # 能力归属冲突 (R2)
  test_gate_coverage.py           # Gate 覆盖率 (R3)
```

### 2.2 测试层次

| 层次 | 对象 | 方式 | 文件 |
|------|------|------|------|
| 单元测试 | `PGCDocument(**data)` | 直接构造 dict 传入 | test_valid_document, test_referential_integrity, test_capability_ownership, test_gate_coverage |
| 集成测试 | `PGCValidator.load_and_validate()` | 写入临时 YAML 文件后加载 | test_valid_document (补充) |

### 2.3 共享 Helper

在 `tests/conftest.py` 中定义共享 fixture：

```python
def make_valid_doc() -> dict:
    """返回一个完全合规的 PGC 文档 dict，可作为所有测试的基线"""

def make_doc(**overrides) -> dict:
    """基于 make_valid_doc()，通过 overrides 增量修改字段"""
```

### 2.4 测试矩阵

#### test_valid_document.py

| 用例 ID | 描述 | 输入 | 预期 |
|---------|------|------|------|
| V-1 | 最小合规文档 | 1 persona + 1 gate + 1 capability + 1 binding | 成功实例化 |
| V-2 | 完整合规文档 | 含 governance_authority 的完整文档 | 成功实例化 |
| V-3 | 多 Persona/Binding | 3 persona + 3 gate + 3 capability + 3 binding | 成功实例化 |
| V-4 | 空 lists | personas=[], gates=[], capabilities=[], bindings=[] | 成功实例化（空文档合法） |
| V-5 | 集成: 从 YAML 文件加载 | 写入临时 YAML → load_and_validate | 成功返回 PGCDocument |

#### test_referential_integrity.py

| 用例 ID | 描述 | 修改 | 预期 |
|---------|------|------|------|
| RI-1 | Binding 引用不存在的 persona_id | persona_id="ghost" | ValueError 含 "Persona" |
| RI-2 | Binding 引用不存在的 gate_id | gate_id="phantom-gate" | ValueError 含 "Governance Gate" |
| RI-3 | Binding 引用不存在的 capability_id | capability_id="phantom-cap" | ValueError 含 "Capability" |
| RI-4 | 多个 Binding 中仅一个引用无效 | 仅第 2 个 binding 的 persona_id 无效 | ValueError |

#### test_capability_ownership.py

| 用例 ID | 描述 | 修改 | 预期 |
|---------|------|------|------|
| CO-1 | Capability 属于 Persona B 但被绑定给 Persona A | owner_persona ≠ binding.persona_id | ValueError 含 "归属冲突" |
| CO-2 | 同一 Capability 被两个不同 Persona 的 Binding 引用 | 两个 binding 使用同一 capability_id | 第二个 ValueError |
| CO-3 | Capability owner 与 binding persona 一致 | owner_persona == binding.persona_id | 成功（基线对照） |

#### test_gate_coverage.py

| 用例 ID | 描述 | 修改 | 预期 |
|---------|------|------|------|
| GC-1 | 有 Gate 但无 Binding | gates 有 1 项, bindings=[] | ValueError 含 "未绑定" |
| GC-2 | 多个 Gate 中仅一个未绑定 | 3 gates + 2 bindings | ValueError 含未绑定 gate id |
| GC-3 | 所有 Gate 均已绑定 | 基线文档 | 成功（基线对照） |

## 3. 执行计划

| 步骤 | 内容 | 产出 |
|------|------|------|
| 1 | 创建 `tests/conftest.py`，定义共享 helper | conftest.py |
| 2 | 编写 `test_valid_document.py` | 5 个用例 |
| 3 | 编写 `test_referential_integrity.py` | 4 个用例 |
| 4 | 编写 `test_capability_ownership.py` | 3 个用例 |
| 5 | 编写 `test_gate_coverage.py` | 3 个用例 |
| 6 | 运行 pytest + 覆盖率报告 | 确认 >= 90% |
| 7 | 清理空文件 test_models.py / test_validator.py | 删除或替换 |
