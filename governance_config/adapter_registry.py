"""Namespaced adapter registry for governance assembly."""

from pgc_adapter.base import BaseAdapter
from pgc_adapter.claude import ClaudeCodeAdapter
from pgc_adapter.trae import TraeAdapter


class AdapterRegistry:
    """Resolve namespaced adapter identifiers to adapter instances."""

    _ADAPTERS = {
        "pgc:claude-code": ClaudeCodeAdapter,
        "pgc:trae": TraeAdapter,
    }

    def get(self, adapter_id: str) -> BaseAdapter:
        adapter_cls = self._ADAPTERS.get(adapter_id)
        if adapter_cls is None:
            available = ", ".join(sorted(self._ADAPTERS))
            raise ValueError(f"Unknown adapter '{adapter_id}'. Available: {available}")
        return adapter_cls()
