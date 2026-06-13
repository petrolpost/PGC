"""
PGC Adapter: BaseAdapter abstract base class.

All runtime adapters must inherit from BaseAdapter and implement
the abstract methods to provide consistent behavior across runtimes.
"""

from abc import ABC, abstractmethod
from typing import Dict, List

from pgc_core.model import PGCDocument


class BaseAdapter(ABC):
    """Abstract base class for all PGC runtime adapters.

    An Adapter translates a platform-agnostic PGCDocument into
    runtime-specific configuration files.
    """

    @abstractmethod
    def render(self, document: PGCDocument) -> Dict[str, str]:
        """Render a PGCDocument into target runtime configuration files.

        Args:
            document: A validated PGC governance document.

        Returns:
            Dict[str, str]: Mapping of relative file path to file content.
            Keys are relative paths (e.g. "CLAUDE.md"), values are full
            file contents as strings.
        """
        ...

    @abstractmethod
    def get_target_runtime(self) -> str:
        """Return the runtime identifier this adapter targets.

        Returns:
            str: Runtime identifier, e.g. "claude-code", "cursor", "langgraph".
        """
        ...

    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """Return the file extensions of generated configuration files.

        Returns:
            List[str]: File extensions, e.g. [".md"], [".json", ".yaml"].
        """
        ...

    def validate_compatibility(self, document: PGCDocument) -> bool:
        """Check whether a PGCDocument meets the minimum requirements for this runtime.

        Default implementation: the document must have at least one persona
        and one governance_binding. Subclasses may override for stricter checks.

        Args:
            document: The PGC document to check.

        Returns:
            bool: True if compatible, False otherwise.
        """
        return len(document.personas) > 0 and len(document.governance_bindings) > 0
