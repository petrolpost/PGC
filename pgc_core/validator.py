"""
PGC Core: Loader and Validation Engine
"""

import re
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import ValidationError

from .model import PGCDocument


class PGCValidationError(Exception):
    """自定义异常，用于清晰区分验证错误和普通 Python 错误"""
    pass


class PGCValidator:
    """PGC 验证引擎"""
    
    @staticmethod
    def load_and_validate(file_path: str) -> PGCDocument:
        """
        从单个 YAML 文件加载并验证 PGC 文档
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PGC 配置文件未找到: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise PGCValidationError(f"YAML 解析失败: {e}")
                
        if not isinstance(data, dict):
            raise PGCValidationError("PGC 配置文件根节点必须是一个 YAML 字典 (Dictionary)。")

        try:
            # 实例化时会自动触发 models.py 中的 @model_validator
            return PGCDocument(**data)
        except ValidationError as e:
            # 将 Pydantic 的错误格式化为更易读的 PGC 专属错误
            error_msgs = []
            for error in e.errors():
                loc = " -> ".join(str(x) for x in error['loc'])
                msg = error['msg']
                error_msgs.append(f"  - [{loc}]: {msg}")
            
            raise PGCValidationError(f"PGC 治理契约验证失败:\n" + "\n".join(error_msgs))

    @staticmethod
    def validate_directory(dir_path: str) -> Dict[str, Any]:
        """
        (未来扩展) 扫描整个目录下的所有 .pgc.yaml 文件并进行验证
        返回验证报告
        """
        path = Path(dir_path)
        results = {"success": [], "failed": []}
        
        for yaml_file in path.rglob("*.pgc.yaml"):
            try:
                PGCValidator.load_and_validate(str(yaml_file))
                results["success"].append(str(yaml_file))
            except (FileNotFoundError, PGCValidationError) as e:
                results["failed"].append({"file": str(yaml_file), "error": str(e)})
                
        return results


def check_runtime_compatibility(
    document: PGCDocument,
    adapter_runtime_version: str,
) -> List[str]:
    """Check if document's target_runtime is compatible with an adapter.

    Args:
        document: The PGC document to check.
        adapter_runtime_version: The adapter's supported version, e.g. "claude-code@1.0".

    Returns:
        List[str]: Warning messages. Empty list means compatible.
    """
    warnings: List[str] = []

    if not document.metadata or not document.metadata.target_runtime:
        return warnings

    doc_spec = document.metadata.target_runtime

    # Parse: "claude-code@>=1.0" -> runtime="claude-code", version_spec=">=1.0"
    doc_match = re.match(r'^([a-zA-Z0-9_-]+)@(.+)$', doc_spec)
    adapter_match = re.match(r'^([a-zA-Z0-9_-]+)@(.+)$', adapter_runtime_version)

    if not doc_match or not adapter_match:
        warnings.append(f"Invalid runtime version format: document='{doc_spec}', adapter='{adapter_runtime_version}'")
        return warnings

    doc_runtime = doc_match.group(1)
    doc_version_spec = doc_match.group(2)
    adapter_runtime = adapter_match.group(1)
    adapter_version_str = adapter_match.group(2)

    # Check runtime name match
    if doc_runtime != adapter_runtime:
        warnings.append(
            f"Runtime mismatch: document targets '{doc_runtime}', "
            f"but adapter supports '{adapter_runtime}'"
        )
        return warnings

    # Simple version compatibility check
    # Extract version number from adapter (e.g. "1.0" from "claude-code@1.0")
    try:
        from packaging.version import Version
        adapter_ver = Version(adapter_version_str)

        # Parse the version specifier (e.g. ">=1.0")
        spec_match = re.match(r'^(>=|>|<=|<|==|!=)(.+)$', doc_version_spec)
        if spec_match:
            op = spec_match.group(1)
            spec_ver = Version(spec_match.group(2))
            compatible = {
                ">=": adapter_ver >= spec_ver,
                ">": adapter_ver > spec_ver,
                "<=": adapter_ver <= spec_ver,
                "<": adapter_ver < spec_ver,
                "==": adapter_ver == spec_ver,
                "!=": adapter_ver != spec_ver,
            }.get(op, True)

            if not compatible:
                warnings.append(
                    f"Version incompatibility: document requires '{doc_runtime}@{doc_version_spec}', "
                    f"but adapter provides '{adapter_runtime}@{adapter_version_str}'"
                )
        else:
            # Exact version match
            if doc_version_spec != adapter_version_str:
                doc_ver = Version(doc_version_spec)
                if doc_ver > adapter_ver:
                    warnings.append(
                        f"Version incompatibility: document requires '{doc_runtime}@{doc_version_spec}', "
                        f"but adapter provides '{adapter_runtime}@{adapter_version_str}'"
                    )
    except Exception:
        # If version parsing fails, skip compatibility check
        pass

    return warnings