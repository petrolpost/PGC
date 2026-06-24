"""Pydantic models for project-level governance configuration."""

from pathlib import Path
from typing import Dict, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator


GovernanceMode = Literal["design-time", "run-time"]


class GovernanceSection(BaseModel):
    """Top-level governance settings."""

    mode: GovernanceMode = Field(default="run-time")
    model_config = ConfigDict(extra="forbid")


class ModuleConfig(BaseModel):
    """Configuration for one mounted governance module."""

    enabled: bool = Field(default=True)
    contract: Path
    adapter: str
    source: Optional[Path] = None
    profile: Optional[str] = None
    integrity_level: Optional[str] = None
    command_surface: Optional[str] = None
    record_format: Optional[str] = None
    startup_capture: Optional[bool] = None
    model_config = ConfigDict(extra="forbid")

    @field_validator("adapter")
    @classmethod
    def adapter_must_be_namespaced(cls, value: str) -> str:
        if ":" not in value:
            raise ValueError("adapter must use <module>:<adapter> format")
        module, adapter = value.split(":", 1)
        if not module or not adapter:
            raise ValueError("adapter must use <module>:<adapter> format")
        return value


class OutputConfig(BaseModel):
    """Output paths for rendered governance files and cache metadata."""

    directory: Path = Field(default=Path("."))
    cache: Path = Field(default=Path(".pgc/cache"))
    model_config = ConfigDict(extra="forbid")


class GovernanceConfig(BaseModel):
    """Project-level governance configuration."""

    governance: GovernanceSection = Field(default_factory=GovernanceSection)
    modules: Dict[str, ModuleConfig] = Field(default_factory=dict)
    output: OutputConfig = Field(default_factory=OutputConfig)
    model_config = ConfigDict(extra="forbid")

    @property
    def mode(self) -> GovernanceMode:
        return self.governance.mode

    @classmethod
    def from_file(cls, path: Path) -> "GovernanceConfig":
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError("governance config root must be a YAML dictionary")
        return cls.model_validate(data)

    def enabled_modules(self) -> Dict[str, ModuleConfig]:
        return {
            name: module
            for name, module in self.modules.items()
            if module.enabled
        }
