"""Test TraeAdapter: PGCDocument → .trae/rules/ rendering."""

import pytest

from pgc_adapter.base import BaseAdapter
from pgc_adapter.trae import TraeAdapter
from pgc_core.model import (
    PGCDocument,
    PGCMetadata,
    AuthorityLevel,
)
from pgc_core.validator import check_runtime_compatibility
from conftest import make_valid_doc, make_multi_doc


@pytest.fixture
def adapter() -> TraeAdapter:
    return TraeAdapter()


@pytest.fixture
def valid_doc() -> PGCDocument:
    return PGCDocument(**make_valid_doc())


@pytest.fixture
def multi_doc() -> PGCDocument:
    return PGCDocument(**make_multi_doc())


class TestTraeAdapterMetadata:
    """TR-1, TR-2, TR-3, TR-4: Adapter metadata and inheritance."""

    # TR-1: Inherits BaseAdapter
    def test_inherits_base_adapter(self, adapter: TraeAdapter) -> None:
        assert isinstance(adapter, BaseAdapter)

    # TR-2: Target runtime
    def test_get_target_runtime(self, adapter: TraeAdapter) -> None:
        assert adapter.get_target_runtime() == "trae"

    # TR-3: Target runtime version
    def test_get_target_runtime_version(self, adapter: TraeAdapter) -> None:
        assert adapter.get_target_runtime_version() == "trae@1.3"

    # TR-4: Supported extensions
    def test_get_supported_extensions(self, adapter: TraeAdapter) -> None:
        assert adapter.get_supported_extensions() == [".md"]


class TestTraeAdapterRender:
    """TR-5 through TR-12: Render output content."""

    # TR-5: render returns correct file paths
    def test_render_returns_trae_rules_paths(self, adapter: TraeAdapter, valid_doc: PGCDocument) -> None:
        result = adapter.render(valid_doc)
        for key in result:
            assert key.startswith(".trae/rules/")

    # TR-6: Persona generates independent files
    def test_persona_generates_independent_file(self, adapter: TraeAdapter, valid_doc: PGCDocument) -> None:
        result = adapter.render(valid_doc)
        assert ".trae/rules/persona-reviewer.md" in result

    def test_multi_persona_generates_multiple_files(self, adapter: TraeAdapter, multi_doc: PGCDocument) -> None:
        result = adapter.render(multi_doc)
        assert ".trae/rules/persona-reviewer.md" in result
        assert ".trae/rules/persona-security-auditor.md" in result
        assert ".trae/rules/persona-deployer.md" in result

    # TR-7: Persona file contains frontmatter
    def test_persona_file_contains_frontmatter(self, adapter: TraeAdapter, valid_doc: PGCDocument) -> None:
        content = adapter.render(valid_doc)[".trae/rules/persona-reviewer.md"]
        assert "---" in content
        assert "alwaysApply: true" in content

    # TR-8: Persona file contains responsibilities
    def test_persona_file_contains_responsibilities(self, adapter: TraeAdapter, valid_doc: PGCDocument) -> None:
        content = adapter.render(valid_doc)[".trae/rules/persona-reviewer.md"]
        assert "## Responsibilities" in content
        assert "审查代码质量" in content

    # TR-9: Boundaries file
    def test_boundaries_file_rendered(self, adapter: TraeAdapter, valid_doc: PGCDocument) -> None:
        result = adapter.render(valid_doc)
        assert ".trae/rules/boundaries.md" in result
        content = result[".trae/rules/boundaries.md"]
        assert "NEVER:" in content
        assert "直接修改代码" in content

    # TR-10: Governance file
    def test_governance_file_rendered(self, adapter: TraeAdapter, valid_doc: PGCDocument) -> None:
        result = adapter.render(valid_doc)
        assert ".trae/rules/governance.md" in result
        content = result[".trae/rules/governance.md"]
        assert "# Governance Rules" in content
        assert "pre-commit-quality" in content

    # TR-10: STRICT violation prompt
    def test_strict_violation_prompt(self, adapter: TraeAdapter, valid_doc: PGCDocument) -> None:
        content = adapter.render(valid_doc)[".trae/rules/governance.md"]
        assert "STOP and ask for human review" in content

    def test_advisory_no_stop_prompt(self, adapter: TraeAdapter) -> None:
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
        content = adapter.render(doc)[".trae/rules/governance.md"]
        assert "STOP and ask for human review" not in content

    # TR-11: Capabilities file with smart activation
    def test_capabilities_file_smart_activation(self, adapter: TraeAdapter, valid_doc: PGCDocument) -> None:
        result = adapter.render(valid_doc)
        assert ".trae/rules/capabilities.md" in result
        content = result[".trae/rules/capabilities.md"]
        assert "alwaysApply: false" in content
        assert "description:" in content

    # TR-12: Empty boundaries does not generate file
    def test_no_boundaries_file_when_empty(self, adapter: TraeAdapter) -> None:
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
        result = adapter.render(doc)
        assert ".trae/rules/boundaries.md" not in result

    def test_no_capabilities_file_when_empty(self, adapter: TraeAdapter) -> None:
        # When there are no capabilities, there can be no bindings referencing them.
        # A valid doc with no capabilities must also have no bindings.
        # This is an edge case: governance_gates with no bindings is invalid (unbound gates),
        # so we test by removing gates and bindings entirely.
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
            governance_gates=[],
            capabilities=[],
            governance_bindings=[],
        )
        result = adapter.render(doc)
        assert ".trae/rules/capabilities.md" not in result


class TestTraeAdapterVersioning:
    """TR-V1 through TR-V5: Version compatibility tests."""

    def _make_doc_with_runtime(self, target_runtime: str) -> PGCDocument:
        data = make_valid_doc()
        data["metadata"] = {"target_runtime": target_runtime}
        return PGCDocument(**data)

    # TR-V1: Compatible version
    def test_compatible_version(self, adapter: TraeAdapter) -> None:
        doc = self._make_doc_with_runtime("trae@>=1.3")
        warnings = check_runtime_compatibility(doc, adapter.get_target_runtime_version())
        assert len(warnings) == 0

    # TR-V2: Document version higher than adapter
    def test_version_too_high(self, adapter: TraeAdapter) -> None:
        doc = self._make_doc_with_runtime("trae@>=2.0")
        warnings = check_runtime_compatibility(doc, adapter.get_target_runtime_version())
        assert len(warnings) > 0

    # TR-V3: Runtime name mismatch
    def test_runtime_name_mismatch(self, adapter: TraeAdapter) -> None:
        doc = self._make_doc_with_runtime("claude-code@>=1.0")
        warnings = check_runtime_compatibility(doc, adapter.get_target_runtime_version())
        assert len(warnings) > 0

    # TR-V4: No metadata — backward compatible
    def test_no_metadata_backward_compatible(self, adapter: TraeAdapter) -> None:
        doc = PGCDocument(**make_valid_doc())
        warnings = check_runtime_compatibility(doc, adapter.get_target_runtime_version())
        assert len(warnings) == 0

    # TR-V5: Empty metadata — backward compatible
    def test_empty_metadata_backward_compatible(self, adapter: TraeAdapter) -> None:
        data = make_valid_doc()
        data["metadata"] = {}
        doc = PGCDocument(**data)
        warnings = check_runtime_compatibility(doc, adapter.get_target_runtime_version())
        assert len(warnings) == 0
