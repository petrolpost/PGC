"""
Issue #1: CLI integration tests for pgc init & pgc validate
Test Plan: docs/issues/1-pgc-cli/test-plan.md
"""

import yaml
from pathlib import Path
from typing import Dict, Any

import pytest
from typer.testing import CliRunner

from pgc_core.cli import app

runner = CliRunner()

# ── Fixture helpers ────────────────────────────────────────────────────

VALID_DOC: Dict[str, Any] = {
    "personas": [
        {
            "id": "developer",
            "name": "Core Developer",
            "responsibilities": ["implement features"],
            "negative_boundaries": ["modify schema without approval"],
            "output_target": "source_code_repository",
        }
    ],
    "governance_gates": [
        {
            "id": "quality-gate",
            "type": "quality",
            "description": "Code must pass static analysis.",
        }
    ],
    "capabilities": [
        {
            "id": "run-tests",
            "owner_persona": "developer",
            "description": "Execute test suites.",
        }
    ],
    "governance_bindings": [
        {
            "gate_id": "quality-gate",
            "persona_id": "developer",
            "capability_id": "run-tests",
            "authority_level": "strict",
        }
    ],
    "governance_authority": {
        "default_violation_policy": "block",
    },
}

# Two-persona doc for ownership conflict tests
TWO_PERSONA_DOC: Dict[str, Any] = {
    "personas": [
        {
            "id": "developer",
            "name": "Core Developer",
            "responsibilities": ["implement features"],
            "negative_boundaries": [],
            "output_target": "source_code_repository",
        },
        {
            "id": "reviewer",
            "name": "Code Reviewer",
            "responsibilities": ["review code"],
            "negative_boundaries": [],
            "output_target": "review_logs",
        },
    ],
    "governance_gates": [
        {
            "id": "quality-gate",
            "type": "quality",
            "description": "Code must pass static analysis.",
        }
    ],
    "capabilities": [
        {
            "id": "run-tests",
            "owner_persona": "developer",
            "description": "Execute test suites.",
        }
    ],
    "governance_bindings": [
        {
            "gate_id": "quality-gate",
            "persona_id": "reviewer",
            "capability_id": "run-tests",
            "authority_level": "strict",
        }
    ],
    "governance_authority": {
        "default_violation_policy": "block",
    },
}


VARIANTS: Dict[str, Dict[str, Any]] = {
    "valid_doc": VALID_DOC,
    "missing_required": {
        "personas": [
            {
                "id": "developer",
                "name": "Core Developer",
                "responsibilities": ["implement features"],
                "negative_boundaries": [],
                # output_target intentionally missing
            }
        ],
        "governance_gates": VALID_DOC["governance_gates"],
        "capabilities": VALID_DOC["capabilities"],
        "governance_bindings": VALID_DOC["governance_bindings"],
        "governance_authority": VALID_DOC["governance_authority"],
    },
    "invalid_persona_ref": {
        **VALID_DOC,
        "governance_bindings": [
            {
                "gate_id": "quality-gate",
                "persona_id": "ghost",
                "capability_id": "run-tests",
                "authority_level": "strict",
            }
        ],
    },
    "invalid_gate_ref": {
        **VALID_DOC,
        "governance_bindings": [
            {
                "gate_id": "ghost",
                "persona_id": "developer",
                "capability_id": "run-tests",
                "authority_level": "strict",
            }
        ],
    },
    "invalid_capability_ref": {
        **VALID_DOC,
        "governance_bindings": [
            {
                "gate_id": "quality-gate",
                "persona_id": "developer",
                "capability_id": "ghost",
                "authority_level": "strict",
            }
        ],
    },
    "capability_ownership_conflict": TWO_PERSONA_DOC,
    "unbound_gate": {
        **VALID_DOC,
        "governance_gates": [
            *VALID_DOC["governance_gates"],
            {"id": "orphan-gate", "type": "security", "description": "No one owns this."},
        ],
    },
}


def write_pgc_yaml(tmp_path: Path, variant: str, filename: str = "agent.pgc.yaml") -> Path:
    """Write a PGC YAML fixture to tmp_path and return the file path."""
    data = VARIANTS[variant]
    file_path = tmp_path / filename
    file_path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return file_path


# ── pgc init tests ─────────────────────────────────────────────────────


class TestInit:
    """Test cases for pgc init command."""

    # I-1: Initialize empty directory
    def test_init_empty_dir(self, tmp_path: Path) -> None:
        target = tmp_path / "new-project"
        result = runner.invoke(app, ["init", str(target)])
        assert result.exit_code == 0
        assert (target / "agent.pgc.yaml").exists()
        assert (target / ".pgc" / "README.md").exists()

    # I-2: Directory already exists and is not empty
    def test_init_nonempty_dir(self, tmp_path: Path) -> None:
        existing = tmp_path / "existing-dir"
        existing.mkdir()
        (existing / "some-file.txt").write_text("hello", encoding="utf-8")
        result = runner.invoke(app, ["init", str(existing)])
        assert result.exit_code == 1
        assert "already exists" in result.output or "not empty" in result.output

    # I-3: Generated template passes validate
    def test_init_then_validate(self, tmp_path: Path) -> None:
        target = tmp_path / "init-project"
        runner.invoke(app, ["init", str(target)])
        result = runner.invoke(app, ["validate", str(target)])
        assert result.exit_code == 0
        assert "[OK]" in result.output

    # I-4: Generated YAML has all 5 top-level keys
    def test_init_template_structure(self, tmp_path: Path) -> None:
        target = tmp_path / "struct-project"
        runner.invoke(app, ["init", str(target)])
        with open(target / "agent.pgc.yaml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        expected_keys = {"personas", "governance_gates", "capabilities", "governance_bindings", "governance_authority"}
        assert expected_keys.issubset(data.keys())


# ── pgc validate tests ─────────────────────────────────────────────────


class TestValidate:
    """Test cases for pgc validate command."""

    # V-1: Validate valid single file
    def test_validate_valid_file(self, tmp_path: Path) -> None:
        f = write_pgc_yaml(tmp_path, "valid_doc")
        result = runner.invoke(app, ["validate", str(f)])
        assert result.exit_code == 0
        assert "[OK]" in result.output

    # V-2: Validate valid directory
    def test_validate_valid_directory(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        write_pgc_yaml(project, "valid_doc")
        result = runner.invoke(app, ["validate", str(project)])
        assert result.exit_code == 0
        assert "[OK]" in result.output

    # V-3: Missing required field
    def test_validate_missing_required(self, tmp_path: Path) -> None:
        f = write_pgc_yaml(tmp_path, "missing_required")
        result = runner.invoke(app, ["validate", str(f)])
        assert result.exit_code == 1
        assert "[FAIL]" in result.output
        assert "Field required" in result.output

    # V-4: Reference to non-existent Persona
    def test_validate_invalid_persona_ref(self, tmp_path: Path) -> None:
        f = write_pgc_yaml(tmp_path, "invalid_persona_ref")
        result = runner.invoke(app, ["validate", str(f)])
        assert result.exit_code == 1
        assert "ghost" in result.output

    # V-5: Reference to non-existent Gate
    def test_validate_invalid_gate_ref(self, tmp_path: Path) -> None:
        f = write_pgc_yaml(tmp_path, "invalid_gate_ref")
        result = runner.invoke(app, ["validate", str(f)])
        assert result.exit_code == 1
        assert "ghost" in result.output

    # V-6: Reference to non-existent Capability
    def test_validate_invalid_capability_ref(self, tmp_path: Path) -> None:
        f = write_pgc_yaml(tmp_path, "invalid_capability_ref")
        result = runner.invoke(app, ["validate", str(f)])
        assert result.exit_code == 1
        assert "ghost" in result.output

    # V-7: Capability ownership conflict
    def test_validate_capability_ownership_conflict(self, tmp_path: Path) -> None:
        f = write_pgc_yaml(tmp_path, "capability_ownership_conflict")
        result = runner.invoke(app, ["validate", str(f)])
        assert result.exit_code == 1
        assert "Capability" in result.output and "归属冲突" in result.output

    # V-8: Unbound gate
    def test_validate_unbound_gate(self, tmp_path: Path) -> None:
        f = write_pgc_yaml(tmp_path, "unbound_gate")
        result = runner.invoke(app, ["validate", str(f)])
        assert result.exit_code == 1
        assert "未绑定" in result.output or "unbound" in result.output.lower()

    # V-9: Path does not exist
    def test_validate_nonexistent_path(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["validate", str(tmp_path / "nonexistent")])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    # V-10: Directory with no .pgc.yaml files
    def test_validate_empty_directory(self, tmp_path: Path) -> None:
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        result = runner.invoke(app, ["validate", str(empty_dir)])
        assert result.exit_code == 1
        assert "No .pgc.yaml" in result.output

    # V-11: Mixed valid and invalid files in directory
    def test_validate_mixed_directory(self, tmp_path: Path) -> None:
        project = tmp_path / "mixed"
        project.mkdir()
        write_pgc_yaml(project, "valid_doc", "valid.pgc.yaml")
        write_pgc_yaml(project, "missing_required", "broken.pgc.yaml")
        result = runner.invoke(app, ["validate", str(project)])
        assert result.exit_code == 1
        assert "[OK]" in result.output
        assert "[FAIL]" in result.output


# ── pgc render tests ───────────────────────────────────────────────────


class TestRender:
    """Test cases for pgc render command."""

    # R-1: Render with claude-code adapter
    def test_render_claude_code(self, tmp_path: Path) -> None:
        f = write_pgc_yaml(tmp_path, "valid_doc")
        out_dir = tmp_path / "output"
        result = runner.invoke(app, ["render", str(f), "--adapter", "claude-code", "--output", str(out_dir)])
        assert result.exit_code == 0
        assert (out_dir / "CLAUDE.md").exists()
        content = (out_dir / "CLAUDE.md").read_text(encoding="utf-8")
        assert "Core Developer" in content
        assert "NEVER" in content

    # R-2: Render with trae adapter
    def test_render_trae(self, tmp_path: Path) -> None:
        f = write_pgc_yaml(tmp_path, "valid_doc")
        out_dir = tmp_path / "output"
        result = runner.invoke(app, ["render", str(f), "--adapter", "trae", "--output", str(out_dir)])
        assert result.exit_code == 0
        assert (out_dir / ".trae" / "rules" / "persona-developer.md").exists()
        assert (out_dir / ".trae" / "rules" / "governance.md").exists()

    # R-3: Invalid adapter name
    def test_render_invalid_adapter(self, tmp_path: Path) -> None:
        f = write_pgc_yaml(tmp_path, "valid_doc")
        result = runner.invoke(app, ["render", str(f), "--adapter", "nonexistent"])
        assert result.exit_code == 1
        assert "Unknown adapter" in result.output

    # R-4: Invalid YAML file
    def test_render_invalid_yaml(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "bad.pgc.yaml"
        bad_file.write_text("invalid: {", encoding="utf-8")
        result = runner.invoke(app, ["render", str(bad_file), "--adapter", "claude-code"])
        assert result.exit_code == 1
        assert "Validation failed" in result.output
