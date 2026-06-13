"""Test referential integrity (Rule R1): bindings must reference existing IDs."""

import copy
import pytest

from pgc_core.model import PGCDocument
from conftest import make_valid_doc, make_multi_doc


class TestReferentialIntegrity:
    """RI-1 ~ RI-4: Binding references to non-existent IDs must raise ValueError."""

    # RI-1: persona_id does not exist
    def test_invalid_persona_ref(self) -> None:
        data = copy.deepcopy(make_valid_doc())
        data["governance_bindings"][0]["persona_id"] = "ghost"
        with pytest.raises(ValueError, match="Persona.*ghost"):
            PGCDocument(**data)

    # RI-2: gate_id does not exist
    def test_invalid_gate_ref(self) -> None:
        data = copy.deepcopy(make_valid_doc())
        data["governance_bindings"][0]["gate_id"] = "phantom-gate"
        with pytest.raises(ValueError, match="Governance Gate.*phantom-gate"):
            PGCDocument(**data)

    # RI-3: capability_id does not exist
    def test_invalid_capability_ref(self) -> None:
        data = copy.deepcopy(make_valid_doc())
        data["governance_bindings"][0]["capability_id"] = "phantom-cap"
        with pytest.raises(ValueError, match="Capability.*phantom-cap"):
            PGCDocument(**data)

    # RI-4: Only one invalid binding among multiple
    def test_one_invalid_among_multiple(self) -> None:
        data = copy.deepcopy(make_multi_doc())
        # Corrupt only the second binding's persona_id
        data["governance_bindings"][1]["persona_id"] = "nonexistent"
        with pytest.raises(ValueError, match="Persona.*nonexistent"):
            PGCDocument(**data)
