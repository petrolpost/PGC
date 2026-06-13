# Issue #11: Adapter 运行时版本化机制 — Test Plan

## 1. 测试范围

| 模块 | 测试文件 | 覆盖内容 |
|------|----------|----------|
| `pgc_core/model.py` | `tests/test_models.py` (扩展) | PGCMetadata 模型、PGCDocument.metadata 字段 |
| `pgc_adapter/base.py` | `tests/test_base_adapter.py` (扩展) | get_target_runtime_version() 抽象方法 |
| `pgc_adapter/claude/generator.py` | `tests/test_claude_adapter.py` (扩展) | ClaudeCodeAdapter.get_target_runtime_version() |
| `pgc_core/validator.py` | `tests/test_validator.py` (扩展) | check_runtime_compatibility() |
| `pgc_core/cli.py` | `tests/test_cli.py` (扩展) | init 模板含 metadata、validate 输出版本警告 |

## 2. 测试用例

### 2.1 PGCMetadata 模型 (M-1 ~ M-3)

| ID | 用例 | 输入 | 预期 |
|----|------|------|------|
| M-1 | 创建含 target_runtime 的 PGCMetadata | `target_runtime="claude-code@>=1.0"` | 成功创建 |
| M-2 | 创建不含 target_runtime 的 PGCMetadata | `{}` | 成功创建，target_runtime=None |
| M-3 | PGCDocument 含 metadata 字段 | `metadata={"target_runtime": "claude-code@>=1.0"}` + 其余字段 | 成功创建 |

### 2.2 BaseAdapter 版本方法 (B-1 ~ B-2)

| ID | 用例 | 输入 | 预期 |
|----|------|------|------|
| B-1 | 未实现 get_target_runtime_version 的子类不可实例化 | `class Bad(BaseAdapter): ...` | TypeError |
| B-2 | 实现所有抽象方法的子类可实例化 | 含 get_target_runtime_version 的完整子类 | 成功 |

### 2.3 ClaudeCodeAdapter 版本方法 (C-1)

| ID | 用例 | 输入 | 预期 |
|----|------|------|------|
| C-1 | get_target_runtime_version 返回正确格式 | `ClaudeCodeAdapter().get_target_runtime_version()` | 匹配 `claude-code@1.0` |

### 2.4 版本兼容性检查 (V-1 ~ V-5)

| ID | 用例 | 输入 | 预期 |
|----|------|------|------|
| V-1 | 文档版本与 Adapter 兼容 | `target_runtime="claude-code@>=1.0"`, adapter 支持 `claude-code@1.0` | 无警告 |
| V-2 | 文档版本高于 Adapter | `target_runtime="claude-code@>=2.0"`, adapter 支持 `claude-code@1.0` | 返回不兼容警告 |
| V-3 | 文档运行时名称不匹配 | `target_runtime="cursor@>=1.0"`, adapter 是 claude-code | 返回运行时不匹配警告 |
| V-4 | 文档无 target_runtime | `metadata=None` | 无警告（向后兼容） |
| V-5 | 文档有 metadata 但无 target_runtime | `metadata={}` | 无警告（向后兼容） |

### 2.5 CLI 集成 (CLI-1 ~ CLI-2)

| ID | 用例 | 输入 | 预期 |
|----|------|------|------|
| CLI-1 | pgc init 生成的模板含 metadata 段 | `pgc init ./test` | agent.pgc.yaml 含 `metadata:` 和 `target_runtime:` |
| CLI-2 | pgc validate 输出版本兼容性信息 | 含 metadata 的有效文档 | 正常验证通过 |

## 3. 测试数据

### 3.1 Fixture 清单

| Fixture ID | 描述 | 用途 |
|------------|------|------|
| `doc_with_runtime` | 含 `metadata.target_runtime: claude-code@>=1.0` 的完整文档 | V-1, CLI-2 |
| `doc_with_high_runtime` | 含 `metadata.target_runtime: claude-code@>=2.0` 的完整文档 | V-2 |
| `doc_with_wrong_runtime` | 含 `metadata.target_runtime: cursor@>=1.0` 的完整文档 | V-3 |
| `doc_no_metadata` | 不含 metadata 字段的完整文档 | V-4 |
| `doc_empty_metadata` | 含 `metadata: {}` 的完整文档 | V-5 |

所有 fixture 在测试代码中通过 helper 函数动态生成。
