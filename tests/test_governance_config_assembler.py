from pathlib import Path

import yaml

from governance_config.assembler import assemble


VALID_PGC_DOC = {
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
    "governance_authority": {"default_violation_policy": "block"},
}


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def test_assemble_renders_configured_pgc_adapter(tmp_path: Path) -> None:
    write_yaml(tmp_path / ".pgc" / "agent.pgc.yaml", VALID_PGC_DOC)
    write_yaml(
        tmp_path / "governance.yaml",
        {
            "governance": {"mode": "run-time"},
            "modules": {
                "pgc": {
                    "enabled": True,
                    "contract": ".pgc/agent.pgc.yaml",
                    "adapter": "pgc:claude-code",
                }
            },
            "output": {"directory": "rendered", "cache": ".pgc/cache"},
        },
    )

    rendered = assemble(tmp_path / "governance.yaml")

    assert set(rendered.keys()) == {"CLAUDE.md"}
    assert "Core Developer" in rendered["CLAUDE.md"]


def test_assemble_ignores_disabled_modules(tmp_path: Path) -> None:
    write_yaml(tmp_path / ".pgc" / "agent.pgc.yaml", VALID_PGC_DOC)
    write_yaml(
        tmp_path / "governance.yaml",
        {
            "modules": {
                "pgc": {
                    "enabled": False,
                    "contract": ".pgc/agent.pgc.yaml",
                    "adapter": "pgc:claude-code",
                }
            }
        },
    )

    assert assemble(tmp_path / "governance.yaml") == {}


def test_assemble_rejects_unknown_adapter(tmp_path: Path) -> None:
    write_yaml(tmp_path / ".pgc" / "agent.pgc.yaml", VALID_PGC_DOC)
    write_yaml(
        tmp_path / "governance.yaml",
        {
            "modules": {
                "pgc": {
                    "enabled": True,
                    "contract": ".pgc/agent.pgc.yaml",
                    "adapter": "pgc:missing",
                }
            }
        },
    )

    try:
        assemble(tmp_path / "governance.yaml")
    except ValueError as exc:
        assert "Unknown adapter" in str(exc)
    else:
        raise AssertionError("Expected unknown adapter failure")


def test_assemble_renders_tgs_file_adapter(tmp_path: Path) -> None:
    write_yaml(tmp_path / ".tgs" / "traceability.yaml", {"traceability": {"level": "L2"}})
    write_yaml(
        tmp_path / "governance.yaml",
        {
            "modules": {
                "tgs": {
                    "enabled": True,
                    "contract": ".tgs/traceability.yaml",
                    "adapter": "tgs:file",
                    "integrity_level": "L2",
                    "command_surface": "slash",
                }
            }
        },
    )

    rendered = assemble(tmp_path / "governance.yaml")

    assert ".tgs/instructions.md" in rendered
    assert ".tgs/audit-report.md" in rendered
    assert "/tgs anchor create" in rendered[".tgs/instructions.md"]
    assert "GitHub Issue-driven Reference" in rendered[".tgs/instructions.md"]
    assert "GitHub Issue-driven delivery is the default GitHub-backed TGS profile" in rendered[
        ".tgs/instructions.md"
    ]
    assert "review outcomes, and merge evidence before closure" in rendered[".tgs/instructions.md"]
    assert "future TGS package format" in rendered[".tgs/instructions.md"]
    assert "Integrity Level: L2" in rendered[".tgs/audit-report.md"]
