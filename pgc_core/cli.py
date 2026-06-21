"""
PGC Core: CLI entry point — pgc init, pgc validate & pgc render.
"""

from pathlib import Path
from typing import Dict, Optional

import typer
from rich.console import Console

from .model import PGCDocument
from .validator import PGCValidator, PGCValidationError, check_runtime_compatibility

app = typer.Typer(
    name="pgc",
    help="PGC (Persona-Governance-Capability) — Agent Governance Schema CLI",
    add_completion=False,
)
console = Console()

INIT_TEMPLATE = """\
# PGC Governance Document
# See: https://github.com/petrolpost/PGC

metadata:
  target_runtime: claude-code@>=1.0

personas:
  - id: agent
    name: Agent
    responsibilities:
      - Define agent responsibilities here
    negative_boundaries:
      - Define absolute prohibitions here
    output_target: output-target

governance_gates:
  - id: quality-gate
    type: quality
    description: Quality must be ensured before proceeding.

capabilities:
  - id: core-capability
    owner_persona: agent
    description: Core capability of this agent.

governance_bindings:
  - gate_id: quality-gate
    persona_id: agent
    capability_id: core-capability
    authority_level: strict

governance_authority:
  default_violation_policy: block
"""


@app.command()
def init(
    dir: Path = typer.Argument(..., help="Target directory to initialize"),
) -> None:
    """Generate a standard agent.pgc.yaml template and .pgc/ directory structure."""
    target = dir.resolve()

    if target.exists() and any(target.iterdir()):
        console.print(f"[red]Error:[/red] Directory '{target}' already exists and is not empty.")
        raise typer.Exit(code=1)

    # Create directory structure
    pgc_dir = target / ".pgc"
    pgc_dir.mkdir(parents=True, exist_ok=True)

    # Write template
    yaml_path = target / "agent.pgc.yaml"
    yaml_path.write_text(INIT_TEMPLATE, encoding="utf-8")

    # Write .pgc/README
    readme_path = pgc_dir / "README.md"
    readme_path.write_text(
        "# .pgc directory\n\nThis directory holds PGC runtime artifacts.\n",
        encoding="utf-8",
    )

    console.print(f"[green][OK] Initialized PGC project in '{target}'[/green]")
    console.print(f"  - {yaml_path.relative_to(target)}")
    console.print(f"  - .pgc/")


@app.command()
def validate(
    path: Path = typer.Argument(..., help="PGC YAML file or directory to validate"),
) -> None:
    """Validate a PGC governance document or directory of documents."""
    target = path.resolve()

    if not target.exists():
        console.print(f"[red]Error:[/red] Path '{target}' not found.")
        raise typer.Exit(code=1)

    if target.is_file():
        _validate_single(target)
    else:
        _validate_directory(target)


def _validate_single(file_path: Path) -> None:
    """Validate a single PGC YAML file."""
    try:
        doc = PGCValidator.load_and_validate(str(file_path))
        console.print(f"[green][OK] {file_path.name}: Valid PGC document[/green]")
        _check_version_warnings(doc)
    except (PGCValidationError, FileNotFoundError) as e:
        console.print(f"[red][FAIL] {file_path.name}:[/red]")
        console.print(f"  {e}")
        raise typer.Exit(code=1)


def _validate_directory(dir_path: Path) -> None:
    """Validate all .pgc.yaml files in a directory."""
    results = PGCValidator.validate_directory(str(dir_path))

    if not results["success"] and not results["failed"]:
        console.print(f"[red]Error:[/red] No .pgc.yaml files found in '{dir_path}'")
        raise typer.Exit(code=1)

    for f in results["success"]:
        console.print(f"[green][OK] {Path(f).name}[/green]")

    for entry in results["failed"]:
        console.print(f"[red][FAIL] {Path(entry['file']).name}:[/red]")
        console.print(f"  {entry['error']}")

    if results["failed"]:
        raise typer.Exit(code=1)


def _check_version_warnings(doc: PGCDocument) -> None:
    """Print version compatibility warnings if applicable."""
    if not doc.metadata or not doc.metadata.target_runtime:
        return

    try:
        from pgc_adapter.claude import ClaudeCodeAdapter
        adapter = ClaudeCodeAdapter()
        warnings = check_runtime_compatibility(doc, adapter.get_target_runtime_version())
        for w in warnings:
            console.print(f"[yellow][WARN] {w}[/yellow]")
    except ImportError:
        pass


# --- Adapter Registry ---

ADAPTER_REGISTRY = {
    "claude-code": "pgc_adapter.claude.ClaudeCodeAdapter",
    "trae": "pgc_adapter.trae.TraeAdapter",
}


def _get_adapter(name: str):
    """Load an adapter class by name from the registry."""
    if name not in ADAPTER_REGISTRY:
        available = ", ".join(sorted(ADAPTER_REGISTRY.keys()))
        console.print(
            f"[red]Error:[/red] Unknown adapter '{name}'. Available: {available}"
        )
        raise typer.Exit(code=1)

    module_path, class_name = ADAPTER_REGISTRY[name].rsplit(".", 1)
    try:
        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, class_name)()
    except (ImportError, AttributeError) as e:
        console.print(f"[red]Error:[/red] Failed to load adapter '{name}': {e}")
        raise typer.Exit(code=1)


@app.command()
def render(
    path: Optional[Path] = typer.Argument(None, help="PGC YAML file to render"),
    adapter: Optional[str] = typer.Option(None, "--adapter", "-a", help="Target adapter name"),
    output: Path = typer.Option(".", "--output", "-o", help="Output directory"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Governance configuration file"),
) -> None:
    """Render governance documents to runtime-specific configuration files."""
    if config is not None:
        try:
            from governance_config.assembler import render_config

            files = render_config(config, output)
        except Exception as e:
            console.print(f"[red]Error:[/red] Config render failed: {e}")
            raise typer.Exit(code=1)

        for rel_path in files:
            console.print(f"  [green]Created:[/green] {rel_path}")
        console.print(f"\n[green][OK] Rendered {len(files)} file(s) to '{output.resolve()}'[/green]")
        return

    if path is None:
        console.print("[red]Error:[/red] Either PATH or --config is required.")
        raise typer.Exit(code=1)

    if adapter is None:
        console.print("[red]Error:[/red] --adapter is required when rendering a PGC YAML file.")
        raise typer.Exit(code=1)

    target = path.resolve()

    if not target.exists():
        console.print(f"[red]Error:[/red] File '{target}' not found.")
        raise typer.Exit(code=1)

    # Validate first
    try:
        doc = PGCValidator.load_and_validate(str(target))
    except (PGCValidationError, FileNotFoundError) as e:
        console.print(f"[red]Error:[/red] Validation failed: {e}")
        raise typer.Exit(code=1)

    # Load adapter and render
    adapter_instance = _get_adapter(adapter)
    files: Dict[str, str] = adapter_instance.render(doc)

    # Write output files
    out_dir = output.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    for rel_path, content in files.items():
        file_path = out_dir / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        console.print(f"  [green]Created:[/green] {rel_path}")

    console.print(f"\n[green][OK] Rendered {len(files)} file(s) to '{out_dir}'[/green]")
