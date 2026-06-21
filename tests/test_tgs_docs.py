from pathlib import Path


REQUIRED_FILES = [
    "tgs/README.md",
    "tgs/traceability-contract.yaml",
    "tgs/instructions.md",
    "tgs/adapters/file.md",
    "tgs/injection/standalone.yaml",
    "tgs/injection/pgc-combined.yaml",
    "tgs/audit/integrity-checker.md",
    "tgs/audit/audit-report-template.md",
]


def test_tgs_documentation_files_exist() -> None:
    for rel_path in REQUIRED_FILES:
        assert Path(rel_path).exists(), rel_path


def test_tgs_readme_defines_core_concepts() -> None:
    content = Path("tgs/README.md").read_text(encoding="utf-8")
    for term in ["Anchor", "Action", "Artifact", "Verification"]:
        assert term in content
    assert "orthogonal to PGC" in content


def test_tgs_examples_use_namespaced_adapter() -> None:
    standalone = Path("tgs/injection/standalone.yaml").read_text(encoding="utf-8")
    combined = Path("tgs/injection/pgc-combined.yaml").read_text(encoding="utf-8")
    assert "adapter: tgs:file" in standalone
    assert "adapter: pgc:claude-code" in combined
    assert "adapter: tgs:file" in combined
