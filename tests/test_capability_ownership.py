"""Test capability ownership (Rule R2): capability owner must match binding persona."""

import copy
import pytest

from pgc_core.model import PGCDocument
from conftest import make_valid_doc, make_multi_doc


class TestCapabilityOwnership:
    """CO-1 ~ CO-3: Capability归属冲突校验."""

    # CO-1: Ownership conflict — capability belongs to B but bound to A
    def test_ownership_conflict(self) -> None:
        data = copy.deepcopy(make_valid_doc())
        # Change capability owner to someone else
        data["capabilities"][0]["owner_persona"] = "other-person"
        with pytest.raises(ValueError, match="归属冲突"):
            PGCDocument(**data)

    # CO-2: Same capability bound by two different personas
    def test_same_capability_two_personas(self) -> None:
        data = copy.deepcopy(make_multi_doc())
        # Second binding reuses first capability but with different persona
        data["governance_bindings"][1]["capability_id"] = "static-analysis"
        # binding[1].persona_id = "security-auditor", but static-analysis owner is "reviewer"
        with pytest.raises(ValueError, match="归属冲突"):
            PGCDocument(**data)

    # CO-3: Ownership consistent (baseline — should succeed)
    def test_ownership_consistent_baseline(self) -> None:
        data = make_valid_doc()
        doc = PGCDocument(**data)
        assert doc.capabilities[0].owner_persona == doc.governance_bindings[0].persona_id
