"""Tests for the journal module in governance assembly."""

from pathlib import Path

import yaml

from governance_config.assembler import assemble


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def test_assemble_renders_journal_file_adapter(tmp_path: Path) -> None:
    write_yaml(tmp_path / ".journal" / "manifest.yaml", {"journal": {"version": "0.1.0"}})
    write_yaml(
        tmp_path / "governance.yaml",
        {
            "modules": {
                "journal": {
                    "enabled": True,
                    "contract": ".journal/manifest.yaml",
                    "adapter": "journal:file",
                    "record_format": "jsonl",
                    "startup_capture": True,
                }
            }
        },
    )

    rendered = assemble(tmp_path / "governance.yaml")

    assert ".journal/manifest.yaml" in rendered
    assert ".journal/events.jsonl" in rendered
    assert ".journal/state.yaml" in rendered
    assert ".journal/handoff.md" in rendered
    assert ".journal/logs/README.md" in rendered


def test_journal_manifest_contains_policy(tmp_path: Path) -> None:
    write_yaml(tmp_path / ".journal" / "manifest.yaml", {"journal": {"version": "0.1.0"}})
    write_yaml(
        tmp_path / "governance.yaml",
        {
            "modules": {
                "journal": {
                    "enabled": True,
                    "contract": ".journal/manifest.yaml",
                    "adapter": "journal:file",
                }
            }
        },
    )

    rendered = assemble(tmp_path / "governance.yaml")

    manifest = rendered[".journal/manifest.yaml"]
    assert "record_format: jsonl" in manifest
    assert "startup_capture: True" in manifest
    assert "append_first: true" in manifest
    assert "handoff_derived: true" in manifest


def test_journal_handoff_is_derived_template(tmp_path: Path) -> None:
    write_yaml(tmp_path / ".journal" / "manifest.yaml", {"journal": {"version": "0.1.0"}})
    write_yaml(
        tmp_path / "governance.yaml",
        {
            "modules": {
                "journal": {
                    "enabled": True,
                    "contract": ".journal/manifest.yaml",
                    "adapter": "journal:file",
                }
            }
        },
    )

    rendered = assemble(tmp_path / "governance.yaml")

    handoff = rendered[".journal/handoff.md"]
    assert "derived from ledger records" in handoff
    assert "Do not edit directly" in handoff
    assert "Task Summary" in handoff
    assert "Current State" in handoff
    assert "Next Steps" in handoff


def test_journal_state_initializes_as_pending(tmp_path: Path) -> None:
    write_yaml(tmp_path / ".journal" / "manifest.yaml", {"journal": {"version": "0.1.0"}})
    write_yaml(
        tmp_path / "governance.yaml",
        {
            "modules": {
                "journal": {
                    "enabled": True,
                    "contract": ".journal/manifest.yaml",
                    "adapter": "journal:file",
                }
            }
        },
    )

    rendered = assemble(tmp_path / "governance.yaml")

    state = rendered[".journal/state.yaml"]
    assert "status: pending" in state
    assert "phase: init" in state


def test_journal_events_starts_empty(tmp_path: Path) -> None:
    write_yaml(tmp_path / ".journal" / "manifest.yaml", {"journal": {"version": "0.1.0"}})
    write_yaml(
        tmp_path / "governance.yaml",
        {
            "modules": {
                "journal": {
                    "enabled": True,
                    "contract": ".journal/manifest.yaml",
                    "adapter": "journal:file",
                }
            }
        },
    )

    rendered = assemble(tmp_path / "governance.yaml")

    assert rendered[".journal/events.jsonl"] == ""


def test_journal_ignores_disabled_module(tmp_path: Path) -> None:
    write_yaml(tmp_path / ".journal" / "manifest.yaml", {"journal": {"version": "0.1.0"}})
    write_yaml(
        tmp_path / "governance.yaml",
        {
            "modules": {
                "journal": {
                    "enabled": False,
                    "contract": ".journal/manifest.yaml",
                    "adapter": "journal:file",
                }
            }
        },
    )

    rendered = assemble(tmp_path / "governance.yaml")

    assert rendered == {}


def test_journal_rejects_unknown_adapter(tmp_path: Path) -> None:
    write_yaml(tmp_path / ".journal" / "manifest.yaml", {"journal": {"version": "0.1.0"}})
    write_yaml(
        tmp_path / "governance.yaml",
        {
            "modules": {
                "journal": {
                    "enabled": True,
                    "contract": ".journal/manifest.yaml",
                    "adapter": "journal:api",
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


def test_journal_rejects_missing_contract(tmp_path: Path) -> None:
    write_yaml(
        tmp_path / "governance.yaml",
        {
            "modules": {
                "journal": {
                    "enabled": True,
                    "contract": ".journal/manifest.yaml",
                    "adapter": "journal:file",
                }
            }
        },
    )

    try:
        assemble(tmp_path / "governance.yaml")
    except FileNotFoundError as exc:
        assert "Journal contract not found" in str(exc)
    else:
        raise AssertionError("Expected missing contract failure")


def test_journal_default_config_values(tmp_path: Path) -> None:
    """When record_format and startup_capture are omitted, defaults are used."""
    write_yaml(tmp_path / ".journal" / "manifest.yaml", {"journal": {"version": "0.1.0"}})
    write_yaml(
        tmp_path / "governance.yaml",
        {
            "modules": {
                "journal": {
                    "enabled": True,
                    "contract": ".journal/manifest.yaml",
                    "adapter": "journal:file",
                }
            }
        },
    )

    rendered = assemble(tmp_path / "governance.yaml")

    manifest = rendered[".journal/manifest.yaml"]
    assert "record_format: jsonl" in manifest
    assert "startup_capture: True" in manifest


def test_journal_custom_record_format(tmp_path: Path) -> None:
    """Custom record_format is reflected in the manifest."""
    write_yaml(tmp_path / ".journal" / "manifest.yaml", {"journal": {"version": "0.1.0"}})
    write_yaml(
        tmp_path / "governance.yaml",
        {
            "modules": {
                "journal": {
                    "enabled": True,
                    "contract": ".journal/manifest.yaml",
                    "adapter": "journal:file",
                    "record_format": "yaml",
                    "startup_capture": False,
                }
            }
        },
    )

    rendered = assemble(tmp_path / "governance.yaml")

    manifest = rendered[".journal/manifest.yaml"]
    assert "record_format: yaml" in manifest
    assert "startup_capture: False" in manifest
