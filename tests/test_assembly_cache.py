from pathlib import Path

import yaml

from governance_config.assembler import render_config


VALID_PGC_DOC = {
    "personas": [
        {
            "id": "developer",
            "name": "Core Developer",
            "responsibilities": ["implement features"],
            "negative_boundaries": [],
            "output_target": "source_code_repository",
        }
    ],
    "governance_gates": [
        {"id": "quality-gate", "type": "quality", "description": "Quality gate."}
    ],
    "capabilities": [
        {"id": "run-tests", "owner_persona": "developer", "description": "Run tests."}
    ],
    "governance_bindings": [
        {
            "gate_id": "quality-gate",
            "persona_id": "developer",
            "capability_id": "run-tests",
            "authority_level": "strict",
        }
    ],
}


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def test_render_config_writes_cache_metadata(tmp_path: Path) -> None:
    write_yaml(tmp_path / ".pgc" / "agent.pgc.yaml", VALID_PGC_DOC)
    write_yaml(
        tmp_path / "governance.yaml",
        {
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

    render_config(tmp_path / "governance.yaml")

    cache_path = tmp_path / ".pgc" / "cache" / "assembly-cache.yaml"
    assert cache_path.exists()
    cache = yaml.safe_load(cache_path.read_text(encoding="utf-8"))
    assert cache["config"] == "governance.yaml"
    assert cache["modules"][0]["name"] == "pgc"
    assert cache["modules"][0]["adapter"] == "pgc:claude-code"
    assert cache["modules"][0]["rendered_files"] == ["CLAUDE.md"]
