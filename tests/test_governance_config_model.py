from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from governance_config.model import GovernanceConfig


def write_config(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "governance.yaml"
    path.write_text(yaml.dump(data, sort_keys=False), encoding="utf-8")
    return path


def minimal_config() -> dict:
    return {
        "governance": {"mode": "run-time"},
        "modules": {
            "pgc": {
                "enabled": True,
                "contract": ".pgc/agent.pgc.yaml",
                "adapter": "pgc:claude-code",
            },
            "tgs": {
                "enabled": False,
                "contract": ".tgs/traceability.yaml",
                "adapter": "tgs:file",
                "integrity_level": "L2",
                "command_surface": "slash",
            },
        },
        "output": {"directory": ".", "cache": ".pgc/cache"},
    }


def test_loads_minimal_config(tmp_path: Path) -> None:
    path = write_config(tmp_path, minimal_config())

    config = GovernanceConfig.from_file(path)

    assert config.mode == "run-time"
    assert config.modules["pgc"].enabled is True
    assert config.modules["pgc"].contract == Path(".pgc/agent.pgc.yaml")
    assert config.modules["pgc"].adapter == "pgc:claude-code"
    assert config.output.directory == Path(".")
    assert config.output.cache == Path(".pgc/cache")


def test_enabled_modules_returns_only_enabled_entries(tmp_path: Path) -> None:
    path = write_config(tmp_path, minimal_config())

    config = GovernanceConfig.from_file(path)

    assert list(config.enabled_modules().keys()) == ["pgc"]


def test_rejects_unknown_mode() -> None:
    data = minimal_config()
    data["governance"]["mode"] = "audit-time"

    with pytest.raises(ValidationError) as exc:
        GovernanceConfig.model_validate(data)

    assert "mode" in str(exc.value)


def test_rejects_non_namespaced_adapter() -> None:
    data = minimal_config()
    data["modules"]["pgc"]["adapter"] = "claude-code"

    with pytest.raises(ValidationError) as exc:
        GovernanceConfig.model_validate(data)

    assert "adapter" in str(exc.value)
    assert "<module>:<adapter>" in str(exc.value)
