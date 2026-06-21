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

    return rendered


def _render_tgs_file(integrity_level: str) -> Dict[str, str]:
    instructions = "\n".join(
        [
            "# TGS Instructions",
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
