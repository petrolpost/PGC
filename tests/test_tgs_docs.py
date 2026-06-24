from pathlib import Path

REQUIRED_FILES = [
    "tgs/README.md",
    "docs/archive/tgs-pgc-embedded-v0/README.md",
    "docs/archive/tgs-pgc-embedded-v0/operating-spec.md",
    "docs/archive/tgs-pgc-embedded-v0/profiles/github-issue-driven.md",
    "docs/archive/tgs-pgc-embedded-v0/traceability-contract.yaml",
    "docs/archive/tgs-pgc-embedded-v0/instructions.md",
    "docs/archive/tgs-pgc-embedded-v0/adapters/file.md",
    "tgs/injection/pgc-combined.yaml",
]


def test_tgs_documentation_files_exist() -> None:
    for rel_path in REQUIRED_FILES:
        assert Path(rel_path).exists(), rel_path


def test_tgs_readme_is_adoption_pointer_not_source_of_truth() -> None:
    content = Path("tgs/README.md").read_text(encoding="utf-8")
    assert "TraceabilityGovernanceSystem" in content
    assert "external TGS project" in content
    assert "not the TGS source of truth" in content
    assert "docs/archive/tgs-pgc-embedded-v0" in content
    assert "Anchor |" not in content
    assert "TGS Core |" not in content


def test_pgc_archives_legacy_embedded_tgs_docs() -> None:
    archived = Path("docs/archive/tgs-pgc-embedded-v0/README.md").read_text(encoding="utf-8")
    assert "TGS: Traceability Governance System" in archived
    assert "TGS Core" in archived


def test_tgs_readme_and_instructions_reference_issue_driven_instance() -> None:
    readme = Path("tgs/README.md").read_text(encoding="utf-8")
    assert "github-issue-driven" in readme
    assert "PGC consumes TGS by configuration reference" in readme
    assert not Path("tgs/instructions.md").exists()


def test_tgs_examples_use_namespaced_adapter() -> None:
    combined = Path("tgs/injection/pgc-combined.yaml").read_text(encoding="utf-8")
    assert "adapter: pgc:claude-code" in combined
    assert "adapter: tgs:file" in combined
    assert "source: ../TraceabilityGovernanceSystem" in combined
    assert "profile: github-issue-driven" in combined
