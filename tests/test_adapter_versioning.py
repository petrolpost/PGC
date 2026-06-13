"""
Issue #11: Adapter runtime versioning tests.
Test Plan: docs/issues/11-adapter-versioning/test-plan.md
"""

import pytest

from pgc_core.model import PGCDocument, PGCMetadata, Persona, GovernanceGate, Capability, GovernanceBinding
from pgc_core.validator import check_runtime_compatibility
from pgc_adapter.base import BaseAdapter
from pgc_adapter.claude import ClaudeCodeAdapter


# ── Shared fixtures ────────────────────────────────────────────────────

def make_doc(target_runtime: str | None = None) -> PGCDocument:
    """Create a minimal valid PGCDocument with optional metadata."""
    metadata = PGCMetadata(target_runtime=target_runtime) if target_runtime else None
    return PGCDocument(
        metadata=metadata,
        personas=[Persona(
            id="agent", name="Agent",
            responsibilities=["act"], negative_boundaries=[], output_target="out",
        )],
        governance_gates=[GovernanceGate(
            id="q-gate", type="quality", description="Quality gate.",
        )],
        capabilities=[Capability(
            id="cap", owner_persona="agent", description="A capability.",
        )],
        governance_bindings=[GovernanceBinding(
            gate_id="q-gate", persona_id="agent", capability_id="cap", authority_level="strict",
        )],
    )


# ── M-1 ~ M-3: PGCMetadata model ─────────────────────────────────────

class TestPGCMetadata:
    # M-1: Create PGCMetadata with target_runtime
    def test_metadata_with_target_runtime(self) -> None:
        meta = PGCMetadata(target_runtime="claude-code@>=1.0")
        assert meta.target_runtime == "claude-code@>=1.0"

    # M-2: Create PGCMetadata without target_runtime
    def test_metadata_without_target_runtime(self) -> None:
        meta = PGCMetadata()
        assert meta.target_runtime is None

    # M-3: PGCDocument with metadata field
    def test_doc_with_metadata(self) -> None:
        doc = make_doc(target_runtime="claude-code@>=1.0")
        assert doc.metadata is not None
        assert doc.metadata.target_runtime == "claude-code@>=1.0"


# ── B-1 ~ B-2: BaseAdapter version method ─────────────────────────────

class TestBaseAdapterVersionMethod:
    # B-1: Subclass without get_target_runtime_version cannot be instantiated
    def test_incomplete_subclass_raises(self) -> None:
        with pytest.raises(TypeError):
            class IncompleteAdapter(BaseAdapter):
                def render(self, document): return {}
                def get_target_runtime(self): return "test"
                def get_supported_extensions(self): return [".txt"]
            IncompleteAdapter()

    # B-2: Complete subclass can be instantiated
    def test_complete_subclass_instantiable(self) -> None:
        class CompleteAdapter(BaseAdapter):
            def render(self, document): return {}
            def get_target_runtime(self): return "test"
            def get_target_runtime_version(self): return "test@1.0"
            def get_supported_extensions(self): return [".txt"]
        adapter = CompleteAdapter()
        assert adapter.get_target_runtime_version() == "test@1.0"


# ── C-1: ClaudeCodeAdapter version method ──────────────────────────────

class TestClaudeCodeAdapterVersion:
    # C-1: Returns correct version format
    def test_version_format(self) -> None:
        adapter = ClaudeCodeAdapter()
        version = adapter.get_target_runtime_version()
        assert version.startswith("claude-code@")
        # Verify version part is valid
        parts = version.split("@")
        assert len(parts) == 2


# ── V-1 ~ V-5: Runtime compatibility checks ───────────────────────────

class TestRuntimeCompatibility:
    # V-1: Compatible version
    def test_compatible_version(self) -> None:
        doc = make_doc(target_runtime="claude-code@>=1.0")
        warnings = check_runtime_compatibility(doc, "claude-code@1.0")
        assert len(warnings) == 0

    # V-2: Document version higher than adapter
    def test_version_too_high(self) -> None:
        doc = make_doc(target_runtime="claude-code@>=2.0")
        warnings = check_runtime_compatibility(doc, "claude-code@1.0")
        assert len(warnings) > 0
        assert "incompatibility" in warnings[0].lower() or "Version" in warnings[0]

    # V-3: Runtime name mismatch
    def test_runtime_mismatch(self) -> None:
        doc = make_doc(target_runtime="cursor@>=1.0")
        warnings = check_runtime_compatibility(doc, "claude-code@1.0")
        assert len(warnings) > 0
        assert "mismatch" in warnings[0].lower()

    # V-4: No metadata (backward compatible)
    def test_no_metadata(self) -> None:
        doc = make_doc(target_runtime=None)
        warnings = check_runtime_compatibility(doc, "claude-code@1.0")
        assert len(warnings) == 0

    # V-5: Metadata without target_runtime (backward compatible)
    def test_empty_metadata(self) -> None:
        doc = PGCDocument(
            metadata=PGCMetadata(),
            personas=[Persona(
                id="agent", name="Agent",
                responsibilities=["act"], negative_boundaries=[], output_target="out",
            )],
            governance_gates=[GovernanceGate(
                id="q-gate", type="quality", description="Quality gate.",
            )],
            capabilities=[Capability(
                id="cap", owner_persona="agent", description="A capability.",
            )],
            governance_bindings=[GovernanceBinding(
                gate_id="q-gate", persona_id="agent", capability_id="cap", authority_level="strict",
            )],
        )
        warnings = check_runtime_compatibility(doc, "claude-code@1.0")
        assert len(warnings) == 0
