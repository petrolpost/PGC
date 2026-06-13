"""Shared fixtures and helpers for PGC core model tests."""

import copy
import pytest
import yaml
from pathlib import Path

from pgc_core.model import PGCDocument


def make_valid_doc() -> dict:
    """Return a minimal valid PGC document dict (baseline for all tests)."""
    return {
        "personas": [
            {
                "id": "reviewer",
                "name": "Code Reviewer",
                "responsibilities": ["审查代码质量"],
                "negative_boundaries": ["直接修改代码"],
                "output_target": "pull-request-review",
            }
        ],
        "governance_gates": [
            {
                "id": "pre-commit-quality",
                "type": "quality",
                "description": "提交前质量检查",
            }
        ],
        "capabilities": [
            {
                "id": "static-analysis",
                "owner_persona": "reviewer",
                "description": "静态代码分析能力",
            }
        ],
        "governance_bindings": [
            {
                "gate_id": "pre-commit-quality",
                "persona_id": "reviewer",
                "capability_id": "static-analysis",
                "authority_level": "strict",
            }
        ],
    }


def make_multi_doc() -> dict:
    """Return a valid PGC document with 3 personas/gates/capabilities/bindings."""
    return {
        "personas": [
            {
                "id": "reviewer",
                "name": "Code Reviewer",
                "responsibilities": ["审查代码质量"],
                "negative_boundaries": ["直接修改代码"],
                "output_target": "pull-request-review",
            },
            {
                "id": "security-auditor",
                "name": "Security Auditor",
                "responsibilities": ["安全审计"],
                "negative_boundaries": ["跳过安全检查"],
                "output_target": "security-report",
            },
            {
                "id": "deployer",
                "name": "Deployer",
                "responsibilities": ["部署发布"],
                "negative_boundaries": ["未经审批部署"],
                "output_target": "deployment-log",
            },
        ],
        "governance_gates": [
            {"id": "pre-commit-quality", "type": "quality", "description": "提交前质量检查"},
            {"id": "security-scan", "type": "security", "description": "安全扫描检查"},
            {"id": "deploy-approval", "type": "business_rule", "description": "部署审批关卡"},
        ],
        "capabilities": [
            {"id": "static-analysis", "owner_persona": "reviewer", "description": "静态代码分析"},
            {"id": "vuln-scan", "owner_persona": "security-auditor", "description": "漏洞扫描"},
            {"id": "deploy-tool", "owner_persona": "deployer", "description": "部署工具"},
        ],
        "governance_bindings": [
            {"gate_id": "pre-commit-quality", "persona_id": "reviewer", "capability_id": "static-analysis"},
            {"gate_id": "security-scan", "persona_id": "security-auditor", "capability_id": "vuln-scan"},
            {"gate_id": "deploy-approval", "persona_id": "deployer", "capability_id": "deploy-tool"},
        ],
    }


def make_doc(**overrides) -> dict:
    """Return a copy of make_valid_doc() with specified overrides applied."""
    data = copy.deepcopy(make_valid_doc())
    data.update(overrides)
    return data


def write_yaml(tmp_path: Path, data: dict, filename: str = "agent.pgc.yaml") -> Path:
    """Write a dict as YAML to tmp_path and return the file path."""
    file_path = tmp_path / filename
    file_path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return file_path
