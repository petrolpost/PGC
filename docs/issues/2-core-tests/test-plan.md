# Issue #2: 测试计划

## 1. 测试范围

| 模块 | 文件 | 测试类型 | 用例数 |
|------|------|----------|--------|
| PGCDocument 合规加载 | test_valid_document.py | 单元 + 集成 | 5 |
| 引用完整性 (R1) | test_referential_integrity.py | 单元 | 4 |
| 能力归属冲突 (R2) | test_capability_ownership.py | 单元 | 3 |
| Gate 覆盖率 (R3) | test_gate_coverage.py | 单元 | 3 |
| **合计** | | | **15** |

## 2. 测试用例

### 2.1 test_valid_document.py

| 用例 ID | 描述 | 输入构造 | 预期结果 | 验证点 |
|---------|------|----------|----------|--------|
| V-1 | 最小合规文档 | 1 persona + 1 gate + 1 capability + 1 binding (authority=None) | `PGCDocument` 实例化成功 | 字段值正确 |
| V-2 | 完整合规文档 | 含 `governance_authority` + `gate_overrides` | 实例化成功 | authority.default_violation_policy == "block" |
| V-3 | 多实体合规 | 3 persona + 3 gate + 3 capability + 3 binding | 实例化成功 | len(doc.personas) == 3 |
| V-4 | 空文档 | 所有 list 为空 | 实例化成功 | 无 binding 无 gate 时无校验错误 |
| V-5 | 从 YAML 文件加载 | 写入 tmp_path → `PGCValidator.load_and_validate()` | 返回 `PGCDocument` | doc.personas[0].id 正确 |

### 2.2 test_referential_integrity.py

| 用例 ID | 描述 | 输入构造 | 预期结果 | 验证点 |
|---------|------|----------|----------|--------|
| RI-1 | persona_id 不存在 | binding.persona_id="ghost" | `ValueError` | 错误消息含 "Persona" 和 "ghost" |
| RI-2 | gate_id 不存在 | binding.gate_id="phantom-gate" | `ValueError` | 错误消息含 "Governance Gate" 和 "phantom-gate" |
| RI-3 | capability_id 不存在 | binding.capability_id="phantom-cap" | `ValueError` | 错误消息含 "Capability" 和 "phantom-cap" |
| RI-4 | 多 Binding 中仅一个无效 | 第 1 个 binding 正常，第 2 个 persona_id 无效 | `ValueError` | 错误消息含无效 ID |

### 2.3 test_capability_ownership.py

| 用例 ID | 描述 | 输入构造 | 预期结果 | 验证点 |
|---------|------|----------|----------|--------|
| CO-1 | 归属冲突 | capability.owner_persona="B", binding.persona_id="A" | `ValueError` | 错误消息含 "归属冲突" |
| CO-2 | 同一 Capability 被两个 Persona 绑定 | 2 个 binding 引用同一 capability_id，但 persona_id 不同 | 第 2 个 binding 触发 `ValueError` | 错误消息含 "归属冲突" |
| CO-3 | 归属一致（基线） | capability.owner_persona == binding.persona_id | 成功 | 对照组，确认正常路径 |

### 2.4 test_gate_coverage.py

| 用例 ID | 描述 | 输入构造 | 预期结果 | 验证点 |
|---------|------|----------|----------|--------|
| GC-1 | 有 Gate 无 Binding | gates=[1项], bindings=[] | `ValueError` | 错误消息含 "未绑定" 和 gate id |
| GC-2 | 部分 Gate 未绑定 | 3 gates + 2 bindings | `ValueError` | 错误消息含未绑定的 gate id |
| GC-3 | 全部 Gate 已绑定（基线） | 基线文档 | 成功 | 对照组 |

## 3. 测试数据

### 3.1 基线文档 (Baseline)

所有测试基于以下最小合规文档，通过 `conftest.py` 中的 `make_valid_doc()` 生成：

```yaml
personas:
  - id: reviewer
    name: Code Reviewer
    responsibilities: [审查代码质量]
    negative_boundaries: [直接修改代码]
    output_target: pull-request-review

governance_gates:
  - id: pre-commit-quality
    type: quality
    description: 提交前质量检查

capabilities:
  - id: static-analysis
    owner_persona: reviewer
    description: 静态代码分析能力

governance_bindings:
  - gate_id: pre-commit-quality
    persona_id: reviewer
    capability_id: static-analysis
    authority_level: strict
```

### 3.2 变异策略

| 变异类型 | 方法 | 用途 |
|----------|------|------|
| 删除字段 | `del data["personas"]` | 缺失必填字段 |
| 替换 ID | `data["governance_bindings"][0]["persona_id"] = "ghost"` | 引用完整性 |
| 修改归属 | `data["capabilities"][0]["owner_persona"] = "other"` | 归属冲突 |
| 删除 Binding | `data["governance_bindings"] = []` | Gate 未绑定 |
| 扩展实体 | 添加第 2/3 个 persona/gate/capability/binding | 多实体场景 |

### 3.3 多实体扩展数据

用于 V-3、RI-4、CO-2、GC-2 等多实体用例：

```yaml
personas:
  - id: reviewer
    name: Code Reviewer
    responsibilities: [审查代码质量]
    negative_boundaries: [直接修改代码]
    output_target: pull-request-review
  - id: security-auditor
    name: Security Auditor
    responsibilities: [安全审计]
    negative_boundaries: [跳过安全检查]
    output_target: security-report
  - id: deployer
    name: Deployer
    responsibilities: [部署发布]
    negative_boundaries: [未经审批部署]
    output_target: deployment-log

governance_gates:
  - id: pre-commit-quality
    type: quality
    description: 提交前质量检查
  - id: security-scan
    type: security
    description: 安全扫描检查
  - id: deploy-approval
    type: business_rule
    description: 部署审批关卡

capabilities:
  - id: static-analysis
    owner_persona: reviewer
    description: 静态代码分析
  - id: vuln-scan
    owner_persona: security-auditor
    description: 漏洞扫描
  - id: deploy-tool
    owner_persona: deployer
    description: 部署工具

governance_bindings:
  - gate_id: pre-commit-quality
    persona_id: reviewer
    capability_id: static-analysis
  - gate_id: security-scan
    persona_id: security-auditor
    capability_id: vuln-scan
  - gate_id: deploy-approval
    persona_id: deployer
    capability_id: deploy-tool
```

## 4. 测试策略

- **运行方式**: `pytest tests/ -v --cov=pgc_core --cov-report=term-missing`
- **覆盖率目标**: pgc_core 模块 >= 90%
- **断言风格**: 使用 `pytest.raises(ValueError, match=...)` 匹配错误消息
- **隔离性**: 每个用例独立构造数据，无测试间依赖
- **集成测试**: V-5 使用 `tmp_path` fixture 写入临时 YAML 文件
