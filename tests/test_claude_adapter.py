"""Test ClaudeCodeAdapter: PGCDocument → CLAUDE.md rendering."""

import pytest

from pgc_adapter.base import BaseAdapter
from pgc_adapter.claude import ClaudeCodeAdapter
from pgc_core.model import PGCDocument, AuthorityLevel, GovernanceAuthority, ViolationPolicy
from conftest import make_valid_doc, make_multi_doc


@pytest.fixture
def adapter() -> ClaudeCodeAdapter:
    return ClaudeCodeAdapter()


@pytest.fixture
def valid_doc() -> PGCDocument:
    return PGCDocument(**make_valid_doc())


@pytest.fixture
def multi_doc() -> PGCDocument:
    return PGCDocument(**make_multi_doc())


class TestClaudeCodeAdapterMetadata:
    """CC-1, CC-2, CC-3: Adapter metadata and inheritance."""

    # CC-1: Inherits BaseAdapter
    def test_inherits_base_adapter(self, adapter: ClaudeCodeAdapter) -> None:
        assert isinstance(adapter, BaseAdapter)

    # CC-2: Target runtime
    def test_get_target_runtime(self, adapter: ClaudeCodeAdapter) -> None:
        assert adapter.get_target_runtime() == "claude-code"

    # CC-3: Supported extensions
    def test_get_supported_extensions(self, adapter: ClaudeCodeAdapter) -> None:
        assert adapter.get_supported_extensions() == [".md"]


class TestClaudeCodeAdapterRender:
    """CC-4 through CC-10: Render output content."""

    # CC-4: render returns CLAUDE.md key
    def test_render_returns_claude_md(self, adapter: ClaudeCodeAdapter, valid_doc: PGCDocument) -> None:
        result = adapter.render(valid_doc)
        assert "CLAUDE.md" in result
        assert isinstance(result["CLAUDE.md"], str)

    # CC-5: Persona mapped to Role & Responsibilities
    def test_persona_mapped_to_roles(self, adapter: ClaudeCodeAdapter, valid_doc: PGCDocument) -> None:
        output = adapter.render(valid_doc)["CLAUDE.md"]
        assert "## Role & Responsibilities" in output
        assert "## Code Reviewer" in output
        assert "审查代码质量" in output

    def test_multi_persona_roles(self, adapter: ClaudeCodeAdapter, multi_doc: PGCDocument) -> None:
        output = adapter.render(multi_doc)["CLAUDE.md"]
        assert "## Code Reviewer" in output
        assert "## Security Auditor" in output
        assert "## Deployer" in output

    # CC-6: negative_boundaries mapped to Absolute Boundaries
    def test_boundaries_rendered(self, adapter: ClaudeCodeAdapter, valid_doc: PGCDocument) -> None:
        output = adapter.render(valid_doc)["CLAUDE.md"]
        assert "## Absolute Boundaries" in output
        assert "NEVER:" in output
        assert "直接修改代码" in output

    def test_no_boundaries_section_when_empty(self, adapter: ClaudeCodeAdapter) -> None:
        doc = PGCDocument(
            personas=[
                {
                    "id": "bot",
                    "name": "Bot",
                    "responsibilities": ["run tasks"],
                    "negative_boundaries": [],
                    "output_target": "stdout",
                }
            ],
            governance_gates=[{"id": "g1", "type": "quality", "description": "check"}],
            capabilities=[{"id": "c1", "owner_persona": "bot", "description": "do stuff"}],
            governance_bindings=[{"gate_id": "g1", "persona_id": "bot", "capability_id": "c1"}],
        )
        output = adapter.render(doc)["CLAUDE.md"]
        assert "## Absolute Boundaries" not in output

    # CC-7: Governance mapped to Governance Rules
    def test_governance_rules_rendered(self, adapter: ClaudeCodeAdapter, valid_doc: PGCDocument) -> None:
        output = adapter.render(valid_doc)["CLAUDE.md"]
        assert "## Governance Rules" in output
        assert "提交前质量检查" in output
        assert "pre-commit-quality" in output

    # CC-8: STRICT violation prompt
    def test_strict_violation_prompt(self, adapter: ClaudeCodeAdapter, valid_doc: PGCDocument) -> None:
        output = adapter.render(valid_doc)["CLAUDE.md"]
        assert "STOP and ask for human review" in output

    def test_advisory_no_stop_prompt(self, adapter: ClaudeCodeAdapter) -> None:
        doc = PGCDocument(
            personas=[
                {
                    "id": "bot",
                    "name": "Bot",
                    "responsibilities": ["run tasks"],
                    "negative_boundaries": [],
                    "output_target": "stdout",
                }
            ],
            governance_gates=[{"id": "g1", "type": "quality", "description": "check"}],
            capabilities=[{"id": "c1", "owner_persona": "bot", "description": "do stuff"}],
            governance_bindings=[
                {
                    "gate_id": "g1",
                    "persona_id": "bot",
                    "capability_id": "c1",
                    "authority_level": "advisory",
                }
            ],
        )
        output = adapter.render(doc)["CLAUDE.md"]
        assert "STOP and ask for human review" not in output

    # CC-9: Output Targets section
    def test_output_targets_rendered(self, adapter: ClaudeCodeAdapter, valid_doc: PGCDocument) -> None:
        output = adapter.render(valid_doc)["CLAUDE.md"]
        assert "## Output Targets" in output
        assert "pull-request-review" in output

    # CC-10: Capabilities section
    def test_capabilities_rendered(self, adapter: ClaudeCodeAdapter, valid_doc: PGCDocument) -> None:
        output = adapter.render(valid_doc)["CLAUDE.md"]
        assert "## Capabilities" in output
        assert "static-analysis" in output
        assert "静态代码分析能力" in output
