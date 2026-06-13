"""Test BaseAdapter abstract base class."""

import pytest
from typing import Dict, List

from pgc_adapter.base import BaseAdapter
from pgc_core.model import PGCDocument
from conftest import make_valid_doc, make_multi_doc


class StubAdapter(BaseAdapter):
    """Minimal concrete implementation for testing ABC constraints."""

    def render(self, document: PGCDocument) -> Dict[str, str]:
        return {"stub.txt": f"personas: {len(document.personas)}"}

    def get_target_runtime(self) -> str:
        return "stub-runtime"

    def get_target_runtime_version(self) -> str:
        return "stub-runtime@1.0"

    def get_supported_extensions(self) -> List[str]:
        return [".txt"]


class IncompleteAdapter(BaseAdapter):
    """Only implements render — missing two abstract methods."""

    def render(self, document: PGCDocument) -> Dict[str, str]:
        return {}


class TestBaseAdapterInstantiation:
    """BA-1, BA-2, BA-3: ABC instantiation constraints."""

    # BA-1: Cannot instantiate BaseAdapter directly
    def test_cannot_instantiate_base(self) -> None:
        with pytest.raises(TypeError):
            BaseAdapter()  # type: ignore[abstract]

    # BA-2: Incomplete subclass cannot be instantiated
    def test_incomplete_subclass_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            IncompleteAdapter()  # type: ignore[abstract]

    # BA-3: Complete subclass can be instantiated
    def test_complete_subclass_instantiates(self) -> None:
        adapter = StubAdapter()
        assert isinstance(adapter, BaseAdapter)


class TestBaseAdapterMethods:
    """BA-4, BA-5: Abstract method return values."""

    # BA-4: render returns Dict[str, str] with correct content
    def test_render_returns_dict(self) -> None:
        adapter = StubAdapter()
        doc = PGCDocument(**make_valid_doc())
        result = adapter.render(doc)
        assert isinstance(result, dict)
        assert "stub.txt" in result
        assert "personas: 1" in result["stub.txt"]

    def test_render_with_multi_doc(self) -> None:
        adapter = StubAdapter()
        doc = PGCDocument(**make_multi_doc())
        result = adapter.render(doc)
        assert "personas: 3" in result["stub.txt"]

    # BA-5: Metadata methods return correct types
    def test_get_target_runtime(self) -> None:
        adapter = StubAdapter()
        assert adapter.get_target_runtime() == "stub-runtime"
        assert isinstance(adapter.get_target_runtime(), str)

    def test_get_supported_extensions(self) -> None:
        adapter = StubAdapter()
        assert adapter.get_supported_extensions() == [".txt"]
        assert isinstance(adapter.get_supported_extensions(), list)


class TestValidateCompatibility:
    """BA-6: validate_compatibility default behavior."""

    def test_empty_doc_not_compatible(self) -> None:
        adapter = StubAdapter()
        doc = PGCDocument(personas=[], governance_gates=[], capabilities=[], governance_bindings=[])
        assert adapter.validate_compatibility(doc) is False

    def test_valid_doc_is_compatible(self) -> None:
        adapter = StubAdapter()
        doc = PGCDocument(**make_valid_doc())
        assert adapter.validate_compatibility(doc) is True
