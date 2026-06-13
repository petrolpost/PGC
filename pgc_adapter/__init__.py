"""PGC Adapter package: runtime-specific configuration generators."""

from .base import BaseAdapter
from .claude import ClaudeCodeAdapter

__all__ = ["BaseAdapter", "ClaudeCodeAdapter"]
