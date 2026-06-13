"""Test gate coverage (Rule R3): every gate must be bound."""

import copy
import pytest

from pgc_core.model import PGCDocument
from conftest import make_valid_doc, make_multi_doc


class TestGateCoverage:
    """GC-1 ~ GC-3: 未绑定的 Gate 必须被拦截."""

    # GC-1: Gate exists but no bindings
    def test_gate_with_no_bindings(self) -> None:
        data = copy.deepcopy(make_valid_doc())
        data["governance_bindings"] = []
        with pytest.raises(ValueError, match="未绑定"):
            PGCDocument(**data)

    # GC-2: Some gates unbound among multiple
    def test_partial_gate_coverage(self) -> None:
        data = copy.deepcopy(make_multi_doc())
        # Remove the third binding, leaving deploy-approval gate unbound
        data["governance_bindings"] = data["governance_bindings"][:2]
        with pytest.raises(ValueError, match="未绑定.*deploy-approval"):
            PGCDocument(**data)

    # GC-3: All gates bound (baseline — should succeed)
    def test_all_gates_bound_baseline(self) -> None:
        data = make_valid_doc()
        doc = PGCDocument(**data)
        bound_gate_ids = {b.gate_id for b in doc.governance_bindings}
        all_gate_ids = {g.id for g in doc.governance_gates}
        assert bound_gate_ids == all_gate_ids
