from pathlib import Path


REQUIRED_FILES = [
    "tgs/README.md",
    "tgs/operating-spec.md",
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
    assert "tgs/operating-spec.md" in content
    for term in ["TGS Core", "TGS Profile", "TGS Adapter", "TGS Package"]:
        assert term in content


def test_tgs_operating_spec_defines_repo_boundary() -> None:
    content = Path("tgs/operating-spec.md").read_text(encoding="utf-8")
    assert "Current State vs Target State" in content
    assert "Layer Boundary In This Repo" in content
    assert "Old Rule Retirement Plan" in content
    assert "L2 by default" in content
    assert "GitHub Object Mapping" in content
    for term in [
        "GitHub Issue",
        "spec.md",
        "test-plan.md",
        "Git commit",
        "Pull request",
        "Review decision or review comment",
        "Merge event",
        "Close event",
    ]:
        assert term in content


def test_tgs_readme_and_instructions_reference_issue_driven_instance() -> None:
    readme = Path("tgs/README.md").read_text(encoding="utf-8")
    instructions = Path("tgs/instructions.md").read_text(encoding="utf-8")
    assert "GitHub Issue-driven delivery as the first concrete GitHub-backed TGS profile" in readme
    assert "GitHub Issue" in readme
    assert "review / merge / test evidence" in readme
    assert "github issue-driven reference" in instructions.lower()
    assert "github issue-driven delivery is the default github-backed tgs profile" in instructions.lower()
    assert "review outcomes, and merge evidence before closure" in instructions
    assert "future tgs package format" in instructions.lower()


def test_tgs_examples_use_namespaced_adapter() -> None:
    standalone = Path("tgs/injection/standalone.yaml").read_text(encoding="utf-8")
    combined = Path("tgs/injection/pgc-combined.yaml").read_text(encoding="utf-8")
    assert "adapter: tgs:file" in standalone
    assert "adapter: pgc:claude-code" in combined
    assert "adapter: tgs:file" in combined
