"""
PGC Core: Loader and Validation Engine
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any
from pydantic import ValidationError

from .models import PGCDocument


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