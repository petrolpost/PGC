"""Config-driven governance assembly."""

import hashlib
from pathlib import Path
from typing import Dict, Optional

import yaml
from pgc_core.validator import PGCValidator

from .adapter_registry import AdapterRegistry
from .model import GovernanceConfig


def assemble(config_path: Path) -> Dict[str, str]:
    """Render all enabled modules from a governance config."""
    config_path = config_path.resolve()
    config = GovernanceConfig.from_file(config_path)
    base_dir = config_path.parent
    registry = AdapterRegistry()
    rendered: Dict[str, str] = {}

    for module_name, module in config.enabled_modules().items():
        if module_name == "pgc":
            contract_path = (base_dir / module.contract).resolve()
            document = PGCValidator.load_and_validate(str(contract_path))
            adapter = registry.get(module.adapter)
            rendered.update(adapter.render(document))
            continue

        if module_name == "tgs":
            if module.adapter != "tgs:file":
                raise ValueError(f"Unknown adapter '{module.adapter}'. Available: tgs:file")
            contract_path = (base_dir / module.contract).resolve()
            if not contract_path.exists():
                raise FileNotFoundError(f"TGS contract not found: {contract_path}")
            rendered.update(_render_tgs_file(module.integrity_level or "L1"))
            continue

        if module_name == "journal":
            if module.adapter != "journal:file":
                raise ValueError(
                    f"Unknown adapter '{module.adapter}'. Available: journal:file"
                )
            contract_path = (base_dir / module.contract).resolve()
            if not contract_path.exists():
                raise FileNotFoundError(f"Journal contract not found: {contract_path}")
            record_format = module.record_format or "jsonl"
            startup_capture = (
                module.startup_capture if module.startup_capture is not None else True
            )
            rendered.update(
                _render_journal_file(
                    record_format=record_format,
                    startup_capture=startup_capture,
                )
            )
            continue

    return rendered


def _render_tgs_file(integrity_level: str) -> Dict[str, str]:
    instructions = "\n".join(
        [
            "# TGS Instructions",
            "",
            "TGS can expose traceability operations through rendered instructions.",
            "",
            "This file defines the instruction surface only. Repository operating policy lives in `tgs/operating-spec.md`.",
            "",
            "## Slash Command Surface",
            "",
            "```text",
            "/tgs anchor create",
            "/tgs action record",
            "/tgs artifact record",
            "/tgs verify",
            "/tgs audit",
            "```",
            "",
            "## Discipline",
            "",
            "- No context, no action.",
            "- No verification, no close.",
            "- No traceability, no completion.",
            "- Preserve ordering between Anchor, Action, Artifact, and Verification.",
            "",
            "## GitHub Issue-driven Reference",
            "",
            "In this repository, GitHub Issue-driven delivery is the default GitHub-backed TGS profile.",
            "",
            "| TGS Operation | GitHub-Backed Reference |",
            "|---|---|",
            "| Anchor | Create or reference the GitHub Issue that authorizes the work. |",
            "| Action | Record issue claim, commit creation, PR submission, and final close actions. |",
            "| Artifact | Link the spec, test plan, changed files, and PR summary or diff. |",
            "| Verification | Link test evidence, review outcomes, and merge evidence before closure. |",
            "",
            "## Boundary",
            "",
            "- Put repository workflow rules in `tgs/operating-spec.md`.",
            "- Keep this file minimal so generated `.tgs/instructions.md` can stay focused on agent-facing operations.",
            "- Do not use this file to redefine TGS Core or a future TGS package format.",
        ]
    )
    audit_report = "\n".join(
        [
            "# TGS Audit Report",
            "",
            "## Summary",
            "",
            "- Anchor:",
            f"- Integrity Level: {integrity_level}",
            "- Result:",
        ]
    )
    return {
        ".tgs/instructions.md": instructions,
        ".tgs/audit-report.md": audit_report,
    }


def _render_journal_file(
    record_format: str = "jsonl",
    startup_capture: bool = True,
) -> Dict[str, str]:
    """Render journal module files: manifest, events, state, handoff, and logs."""
    manifest = "\n".join(
        [
            "# Journal Manifest",
            "",
            "## Task Identity",
            "",
            "- task_id: (auto)",
            "- created_at: (auto)",
            "- resumed_at: (auto)",
            "",
            "## Ledger Policy",
            "",
            f"- record_format: {record_format}",
            f"- startup_capture: {startup_capture}",
            "- append_first: true",
            "- handoff_derived: true",
        ]
    )

    events = ""

    state = "\n".join(
        [
            "# Task State",
            "",
            "## Current",
            "",
            "- status: pending",
            "- phase: init",
            "- progress: 0%",
        ]
    )

    handoff = "\n".join(
        [
            "# Handoff Note",
            "",
            "> This file is derived from ledger records.",
            "> Do not edit directly -- update events.jsonl and regenerate.",
            "",
            "## Task Summary",
            "",
            "(auto-generated)",
            "",
            "## Current State",
            "",
            "(auto-generated)",
            "",
            "## Next Steps",
            "",
            "(auto-generated)",
        ]
    )

    logs_readme = "\n".join(
        [
            "# Logs",
            "",
            "This directory stores raw startup information, error output, and verification output.",
        ]
    )

    return {
        ".journal/manifest.yaml": manifest,
        ".journal/events.jsonl": events,
        ".journal/state.yaml": state,
        ".journal/handoff.md": handoff,
        ".journal/logs/README.md": logs_readme,
    }


def render_config(config_path: Path, output: Optional[Path] = None) -> Dict[str, str]:
    """Render configured modules and write files to disk."""
    config_path = config_path.resolve()
    config = GovernanceConfig.from_file(config_path)
    files = assemble(config_path)
    out_dir = (output or (config_path.parent / config.output.directory)).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    for rel_path, content in files.items():
        file_path = out_dir / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    _write_cache_metadata(config_path, files)

    return files


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_cache_metadata(config_path: Path, output_files: Dict[str, str]) -> None:
    config = GovernanceConfig.from_file(config_path)
    base_dir = config_path.parent
    cache_dir = (base_dir / config.output.cache).resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)

    modules = []
    for module_name, module in config.enabled_modules().items():
        contract_path = (base_dir / module.contract).resolve()
        modules.append(
            {
                "name": module_name,
                "contract": str(module.contract),
                "adapter": module.adapter,
                "contract_hash": _sha256_file(contract_path) if contract_path.exists() else None,
                "rendered_files": sorted(output_files.keys()),
            }
        )

    metadata = {
        "config": config_path.name,
        "config_hash": _sha256_file(config_path),
        "modules": modules,
    }

    (cache_dir / "assembly-cache.yaml").write_text(
        yaml.dump(metadata, sort_keys=False),
        encoding="utf-8",
    )
