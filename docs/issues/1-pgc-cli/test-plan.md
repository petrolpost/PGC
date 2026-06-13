# Issue #1: Test Plan — pgc-core CLI

**关联 Spec**: [spec.md](./spec.md)
**测试代码**: `tests/test_cli.py`

---

## 1. 测试范围

| 模块 | 测试文件 | 类型 |
|------|----------|------|
| `pgc init` | `tests/test_cli.py` | CLI 集成测试 (typer.testing.CliRunner) |
| `pgc validate` | `tests/test_cli.py` | CLI 集成测试 |
| `PGCValidator` | `tests/test_validator.py` | 单元测试 (Issue #2 范围) |
| `PGCDocument` 模型 | `tests/test_models.py` | 单元测试 (Issue #2 范围) |

---

## 2. 测试用例

### 2.1 `pgc init`

| ID | 用例 | 输入 | 预期结果 | 优先级 |
|----|------|------|----------|--------|
| I-1 | 初始化空目录 | `pgc init ./new-project` | 生成 `agent.pgc.yaml` + `.pgc/README.md`，exit 0 | P0 |
| I-2 | 目录已存在且非空 | `pgc init ./existing-dir` (含文件) | 报错 "already exists and is not empty"，exit 1 | P0 |
| I-3 | 生成的模板可通过 validate | `pgc init` → `pgc validate` | validate 输出 Success，exit 0 | P0 |
| I-4 | 生成的 YAML 结构完整 | 检查模板内容 | 包含 personas, governance_gates, capabilities, governance_bindings, governance_authority 五个顶层 key | P1 |

### 2.2 `pgc validate`

| ID | 用例 | 输入 | 预期结果 | 优先级 |
|----|------|------|----------|--------|
| V-1 | 验证合规的单文件 | `pgc validate agent.pgc.yaml` | 输出 [OK] Success，exit 0 | P0 |
| V-2 | 验证合规的目录 | `pgc validate ./project/` | 递归扫描 `.pgc.yaml` 文件，全部 Success，exit 0 | P0 |
| V-3 | 缺少 required 字段 | 删除 `output_target` | 报错 "Field required"，exit 1 | P0 |
| V-4 | 引用不存在的 Persona | binding 中 `persona_id: ghost` | 报错 "引用了不存在的 Persona"，exit 1 | P0 |
| V-5 | 引用不存在的 Gate | binding 中 `gate_id: ghost` | 报错 "引用了不存在的 Governance Gate"，exit 1 | P0 |
| V-6 | 引用不存在的 Capability | binding 中 `capability_id: ghost` | 报错 "引用了不存在的 Capability"，exit 1 | P0 |
| V-7 | Capability 归属冲突 | capability 属于 persona A，但 binding 绑给 persona B | 报错 "Capability 归属冲突"，exit 1 | P0 |
| V-8 | 未绑定的 Gate | 定义了 gate 但无 binding | 报错 "未绑定的 Governance Gate"，exit 1 | P0 |
| V-9 | 路径不存在 | `pgc validate ./nonexistent` | 报错 "Path not found"，exit 1 | P1 |
| V-10 | 目录中无 .pgc.yaml 文件 | 空目录 | 报错 "No .pgc.yaml files found"，exit 1 | P1 |
| V-11 | 目录中混合合规与不合规文件 | 1 个合规 + 1 个不合规 | 表格中 1 个 [OK] + 1 个 [FAIL]，exit 1 | P1 |

---

## 3. 测试数据

测试用例需要以下 YAML fixture，在 `tests/test_cli.py` 中通过 helper 函数动态生成到 `tmp_path`。

### 3.1 Fixture 清单

| Fixture ID | 描述 | 用途 | 对应用例 |
|------------|------|------|----------|
| `valid_doc` | 完整合规的 PGC 文档（含全部 5 个顶层 key） | 合规验证基线 | I-3, V-1, V-2, V-11 |
| `missing_required` | 删除 `output_target` 字段 | required 字段缺失 | V-3 |
| `invalid_persona_ref` | binding 中 `persona_id: ghost` | 引用完整性 - Persona | V-4 |
| `invalid_gate_ref` | binding 中 `gate_id: ghost` | 引用完整性 - Gate | V-5 |
| `invalid_capability_ref` | binding 中 `capability_id: ghost` | 引用完整性 - Capability | V-6 |
| `capability_ownership_conflict` | capability 属于 persona A，binding 绑给 persona B | 归属冲突 | V-7 |
| `unbound_gate` | 定义了 gate 但无对应 binding | Gate 覆盖率 | V-8 |

### 3.2 Fixture 生成策略

- **基线**: `valid_doc` 作为所有 fixture 的起点，通过修改特定字段派生错误变体
- **生成方式**: 在 `tests/test_cli.py` 中定义 `write_pgc_yaml(tmp_path, variant)` helper，接收变体名，写入对应 YAML 并返回文件路径
- **不使用静态文件**: 所有 fixture 动态生成，避免 `tests/fixtures/` 目录维护负担

### 3.3 `valid_doc` 基线内容

```yaml
personas:
  - id: developer
    name: Core Developer
    responsibilities: [implement features]
    negative_boundaries: [modify schema without approval]
    output_target: source_code_repository

governance_gates:
  - id: quality-gate
    type: quality
    description: Code must pass static analysis.

capabilities:
  - id: run-tests
    owner_persona: developer
    description: Execute test suites.

governance_bindings:
  - gate_id: quality-gate
    persona_id: developer
    capability_id: run-tests
    authority_level: strict

governance_authority:
  default_violation_policy: block
```

---

## 4. 测试策略

- 使用 `typer.testing.CliRunner` 进行 CLI 集成测试，无需真实终端
- 使用 `tmp_path` fixture 创建临时目录，测试后自动清理
- 验证错误场景时，检查 exit code 和输出文本（不依赖 Rich 渲染格式）
