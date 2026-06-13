"""
PGC Core: Agent Governance Schema Models
Version: 0.3.0 (Governance-First Edition)
"""

from enum import Enum
from typing import List, Optional, Dict, Set
from pydantic import BaseModel, Field, model_validator, ConfigDict


class GateType(str, Enum):
    SECURITY = "security"
    QUALITY = "quality"
    COMPLIANCE = "compliance"
    BUSINESS_RULE = "business_rule"

class AuthorityLevel(str, Enum):
    STRICT = "strict"      # 必须满足，否则阻断 (Block)
    ADVISORY = "advisory"  # 建议满足，仅记录警告 (Warn/Log)

class ViolationPolicy(str, Enum):
    BLOCK = "block"
    WARN = "warn"
    LOG = "log"


class Persona(BaseModel):
    id: str = Field(..., description="唯一标识，如 'code-reviewer'")
    name: str = Field(..., description="人类可读的名称")
    responsibilities: List[str] = Field(..., description="明确的职责列表")
    negative_boundaries: List[str] = Field(default_factory=list, description="绝对禁止的行为边界")
    output_target: str = Field(..., description="交付物去向")
    model_config = ConfigDict(extra="forbid")


class GovernanceGate(BaseModel):
    id: str = Field(..., description="唯一标识，如 'pre-commit-quality-gate'")
    type: GateType = Field(..., description="约束类别")
    description: str = Field(..., description="人类可读的约束定义")
    model_config = ConfigDict(extra="forbid")


class Capability(BaseModel):
    id: str = Field(..., description="唯一标识，如 'static-code-analysis'")
    owner_persona: str = Field(..., description="拥有/提供此能力的 Persona ID")
    description: str = Field(..., description="该能力能达成什么治理目标")
    model_config = ConfigDict(extra="forbid")


class GovernanceBinding(BaseModel):
    gate_id: str = Field(..., description="关联的 Governance Gate ID")
    persona_id: str = Field(..., description="负责该关卡的 Persona ID")
    capability_id: str = Field(..., description="用于满足该关卡的 Capability ID")
    authority_level: AuthorityLevel = Field(default=AuthorityLevel.STRICT, description="约束严格程度")
    model_config = ConfigDict(extra="forbid")


class GovernanceAuthority(BaseModel):
    default_violation_policy: ViolationPolicy = Field(default=ViolationPolicy.BLOCK)
    gate_overrides: Dict[str, ViolationPolicy] = Field(default_factory=dict)


class PGCDocument(BaseModel):
    """PGC 治理契约根文档"""
    personas: List[Persona] = Field(default_factory=list)
    governance_gates: List[GovernanceGate] = Field(default_factory=list)
    capabilities: List[Capability] = Field(default_factory=list)
    governance_bindings: List[GovernanceBinding] = Field(default_factory=list)
    governance_authority: Optional[GovernanceAuthority] = Field(default=None)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode='after')
    def validate_governance_integrity(self) -> 'PGCDocument':
        """
        核心验证规则 1 & 2:
        1. Referential Integrity (引用完整性)
        2. Capability Ownership (能力归属校验)
        """
        persona_ids = {p.id for p in self.personas}
        gate_ids = {g.id for g in self.governance_gates}
        capability_map = {c.id: c for c in self.capabilities}
        bound_gate_ids = set()

        for binding in self.governance_bindings:
            if binding.persona_id not in persona_ids:
                raise ValueError(f"Binding 引用了不存在的 Persona: '{binding.persona_id}'")
            if binding.gate_id not in gate_ids:
                raise ValueError(f"Binding 引用了不存在的 Governance Gate: '{binding.gate_id}'")
            if binding.capability_id not in capability_map:
                raise ValueError(f"Binding 引用了不存在的 Capability: '{binding.capability_id}'")
            
            # 规则 2: 绑定的 Capability 必须属于声明负责该 Gate 的 Persona
            capability = capability_map[binding.capability_id]
            if capability.owner_persona != binding.persona_id:
                raise ValueError(
                    f"Capability 归属冲突: Capability '{binding.capability_id}' 属于 Persona '{capability.owner_persona}', "
                    f"但被绑定给了 Persona '{binding.persona_id}' 负责 Gate '{binding.gate_id}'。"
                )
            bound_gate_ids.add(binding.gate_id)

        # 规则 3: Gate Coverage (每个 Gate 必须有责任人)
        unbound_gates = gate_ids - bound_gate_ids
        if unbound_gates:
            raise ValueError(f"发现未绑定的 Governance Gate (缺乏责任归属): {', '.join(unbound_gates)}。")

        return self