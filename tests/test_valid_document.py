"""Test valid PGC document loading (baseline + integration)."""

import pytest

from pgc_core.model import PGCDocument
from pgc_core.validator import PGCValidator
from conftest import make_valid_doc, make_multi_doc, make_doc, write_yaml


class TestValidDocument:
    """V-1 ~ V-4: Unit tests for PGCDocument instantiation."""

    # V-1: Minimal valid document
    def test_minimal_valid_doc(self) -> None:
        data = make_valid_doc()
        doc = PGCDocument(**data)
        assert doc.personas[0].id == "reviewer"
        assert doc.governance_gates[0].id == "pre-commit-quality"
        assert doc.capabilities[0].id == "static-analysis"
        assert doc.governance_bindings[0].gate_id == "pre-commit-quality"

    # V-2: Complete document with governance_authority
    def test_complete_doc_with_authority(self) -> None:
        data = make_doc(
            governance_authority={
                "default_violation_policy": "block",
                "gate_overrides": {"pre-commit-quality": "warn"},
            }
        )
        doc = PGCDocument(**data)
        assert doc.governance_authority is not None
        assert doc.governance_authority.default_violation_policy.value == "block"
        assert doc.governance_authority.gate_overrides["pre-commit-quality"].value == "warn"

    # V-3: Multi-entity valid document
    def test_multi_entity_valid_doc(self) -> None:
        data = make_multi_doc()
        doc = PGCDocument(**data)
        assert len(doc.personas) == 3
        assert len(doc.governance_gates) == 3
        assert len(doc.capabilities) == 3
        assert len(doc.governance_bindings) == 3

    # V-4: Empty document (all lists empty)
    def test_empty_doc(self) -> None:
        doc = PGCDocument(personas=[], governance_gates=[], capabilities=[], governance_bindings=[])
        assert doc.personas == []
        assert doc.governance_gates == []
        assert doc.capabilities == []
        assert doc.governance_bindings == []


class TestValidDocumentIntegration:
    """V-5: Integration test — load from YAML file via PGCValidator."""

    def test_load_from_yaml(self, tmp_path) -> None:
        data = make_valid_doc()
        yaml_path = write_yaml(tmp_path, data)
        doc = PGCValidator.load_and_validate(str(yaml_path))
        assert isinstance(doc, PGCDocument)
        assert doc.personas[0].id == "reviewer"
