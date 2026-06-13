# Issue #3: 设计并实现 BaseAdapter 抽象层

## 1. 需求分析

### 1.1 背景

PGC 的核心价值链是：**PGCDocument (YAML) → Adapter → Runtime 配置文件**。Adapter 层负责将平台无关的治理契约翻译为特定运行时的配置格式（如 Claude Code 的 `CLAUDE.md`、Cursor 的 `.cursorrules`）。

当前 `pgc_adapter/base.py` 和 `pgc_adapter/claude/generator.py` 均为空文件，需要先定义统一的抽象接口，确保所有 Adapter 行为一致，便于未来扩展。

### 1.2 目标

1. 定义 `BaseAdapter` 抽象基类 (ABC)，作为所有运行时 Adapter 的契约
2. 核心渲染方法 `render()` 将 `PGCDocument` 转换为 `{文件名: 文件内容}` 的映射
3. 元数据方法声明 Adapter 的目标运行时和支持的文件扩展名
4. 类型提示完整，可通过 mypy 严格模式检查

### 1.3 约束

- `BaseAdapter` 是纯抽象层，不包含具体渲染逻辑
- 所有子类必须实现全部抽象方法，否则实例化时抛出 `TypeError`
- `render()` 返回 `Dict[str, str]`，key 为相对文件路径，value 为文件内容
- 不依赖 IO 操作，Adapter 只负责数据转换

## 2. 设计方案

### 2.1 类图

```
BaseAdapter (ABC)
  ├── render(document: PGCDocument) -> Dict[str, str]   # 抽象方法
  ├── get_target_runtime() -> str                        # 抽象方法
  ├── get_supported_extensions() -> List[str]             # 抽象方法
  └── validate_compatibility(document: PGCDocument) -> bool  # 具体方法（带默认实现）
        └── 检查 document 是否包含该 runtime 所需的最小字段集

ClaudeCodeAdapter (BaseAdapter)   ← Issue #4 实现
  ├── render() -> {"CLAUDE.md": "..."}
  ├── get_target_runtime() -> "claude-code"
  └── get_supported_extensions() -> [".md"]
```

### 2.2 接口定义

```python
from abc import ABC, abstractmethod
from typing import Dict, List

from pgc_core.model import PGCDocument


class BaseAdapter(ABC):
    """所有 PGC Runtime Adapter 的抽象基类。"""

    @abstractmethod
    def render(self, document: PGCDocument) -> Dict[str, str]:
        """
        将 PGCDocument 渲染为目标运行时的配置文件集合。

        Args:
            document: 已验证的 PGC 治理契约文档

        Returns:
            Dict[str, str]: 文件名 → 文件内容的映射。
            key 为相对路径（如 "CLAUDE.md"），value 为完整文件内容。
        """
        ...

    @abstractmethod
    def get_target_runtime(self) -> str:
        """
        返回此 Adapter 目标的运行时标识符。

        Returns:
            str: 运行时标识，如 "claude-code", "cursor", "langgraph"
        """
        ...

    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        返回此 Adapter 生成的配置文件的扩展名列表。

        Returns:
            List[str]: 文件扩展名，如 [".md"], [".json", ".yaml"]
        """
        ...

    def validate_compatibility(self, document: PGCDocument) -> bool:
        """
        检查 PGCDocument 是否包含此运行时所需的最小字段集。

        默认实现：检查 document 至少有 1 个 persona 和 1 个 governance_binding。
        子类可覆盖以添加更严格的检查。

        Args:
            document: 待检查的 PGC 文档

        Returns:
            bool: True 表示兼容，False 表示不兼容
        """
        return len(document.personas) > 0 and len(document.governance_bindings) > 0
```

### 2.3 设计决策

| 决策 | 选项 | 选择 | 理由 |
|------|------|------|------|
| render 返回类型 | `str` / `Dict[str, str]` / `List[FileArtifact]` | `Dict[str, str]` | 简单直接，一个 Adapter 可能生成多个文件（如 Cursor 需要 `.cursorrules` + `.cursorignore`） |
| validate_compatibility 是否抽象 | 抽象 / 具体默认 | 具体默认 | 大多数 Adapter 共享相同的最小检查，避免重复代码 |
| 是否包含 IO 写入 | 是 / 否 | 否 | Adapter 只负责数据转换，写入由调用方决定，保持单一职责 |
| 是否使用 dataclass | 是 / 否 | 否 | ABC 更适合定义行为契约，dataclass 适合数据容器 |

### 2.4 文件结构

```
pgc_adapter/
  __init__.py          # 导出 BaseAdapter
  base.py              # BaseAdapter ABC
  claude/
    __init__.py
    generator.py       # ClaudeCodeAdapter (Issue #4)
```

## 3. 执行计划

| 步骤 | 内容 | 产出 |
|------|------|------|
| 1 | 实现 `pgc_adapter/base.py` | BaseAdapter ABC |
| 2 | 更新 `pgc_adapter/__init__.py` | 导出 BaseAdapter |
| 3 | 编写 `tests/test_base_adapter.py` | 测试用例 |
| 4 | 运行 pytest + mypy 检查 | 确认通过 |
| 5 | 提交 commit 并推送 | PR |
