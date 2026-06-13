"""
PGC Adapter: TraeAdapter — translates PGCDocument into .trae/rules/ files.

Generates Trae IDE-compatible rule files with YAML frontmatter that encode
governance rules as runtime constraints.
"""

from typing import Dict, List

from pgc_adapter.base import BaseAdapter
from pgc_core.model import (
    PGCDocument,
    Persona,
    AuthorityLevel,
    ViolationPolicy,
)


class TraeAdapter(BaseAdapter):
    """Translates PGCDocument into Trae IDE's .trae/rules/ format."""

    RULES_DIR = ".trae/rules"

    def render(self, document: PGCDocument) -> Dict[str, str]:
        """Render PGCDocument to .trae/rules/ files.

        Args:
            document: A validated PGC governance document.

        Returns:
            Dict[str, str]: Mapping of relative file path to file content.
        """
        output: Dict[str, str] = {}

        # Persona files
        for persona in document.personas:
            path = f"{self.RULES_DIR}/persona-{persona.id}.md"
            output[path] = self._render_persona(persona)

        # Boundaries file (skip if empty)
        boundaries = self._render_boundaries(document.personas)
        if boundaries:
            output[f"{self.RULES_DIR}/boundaries.md"] = boundaries

        # Governance file
        output[f"{self.RULES_DIR}/governance.md"] = self._render_governance(document)

        # Capabilities file (skip if empty)
        capabilities = self._render_capabilities(document.capabilities)
        if capabilities:
            output[f"{self.RULES_DIR}/capabilities.md"] = capabilities

        return output

    def get_target_runtime(self) -> str:
        """Return the runtime identifier."""
        return "trae"

    def get_target_runtime_version(self) -> str:
        """Return the supported Trae runtime version.

        .rules frontmatter (alwaysApply, description, globs) was introduced
        in Trae IDE v1.3.0.
        """
        return "trae@1.3"

    def get_supported_extensions(self) -> List[str]:
        """Return supported file extensions."""
        return [".md"]

    # --- Private rendering methods ---

    def _render_persona(self, persona: Persona) -> str:
        lines = [
            "---",
            "alwaysApply: true",
            "---",
            "",
            f"# {persona.name} (`{persona.id}`)",
            "",
            "## Responsibilities",
            "",
        ]
        for r in persona.responsibilities:
            lines.append(f"- {r}")
        lines.append("")
        lines.append(f"## Output Target")
        lines.append("")
        lines.append(persona.output_target)
        return "\n".join(lines)

    def _render_boundaries(self, personas: List[Persona]) -> str:
        all_boundaries: List[str] = []
        for p in personas:
            for b in p.negative_boundaries:
                all_boundaries.append(f"- **[{p.name}]** NEVER: {b}")

        if not all_boundaries:
            return ""

        lines = [
            "---",
            "alwaysApply: true",
            "---",
            "",
            "# Absolute Boundaries",
            "",
            "> **NEVER** violate these boundaries under any circumstances.",
            "",
        ]
        lines.extend(all_boundaries)
        return "\n".join(lines)

    def _render_governance(self, document: PGCDocument) -> str:
        gate_map = {g.id: g for g in document.governance_gates}
        authority = document.governance_authority
        has_strict = False

        rows: List[str] = []
        for binding in document.governance_bindings:
            gate = gate_map.get(binding.gate_id)
            if not gate:
                continue

            # Resolve violation policy
            if authority and binding.gate_id in authority.gate_overrides:
                policy = authority.gate_overrides[binding.gate_id].value
            elif authority:
                policy = authority.default_violation_policy.value
            else:
                policy = ViolationPolicy.BLOCK.value

            authority_label = binding.authority_level.value
            if binding.authority_level == AuthorityLevel.STRICT:
                has_strict = True

            rows.append(
                f"| {gate.description} | `{gate.id}` | {authority_label} | {policy} |"
            )

        lines = [
            "---",
            "alwaysApply: true",
            "---",
            "",
            "# Governance Rules",
            "",
            "| Rule | Gate | Authority | On Violation |",
            "|------|------|-----------|-------------|",
        ]
        lines.extend(rows)

        if has_strict:
            lines.append("")
            lines.append(
                "> When a STRICT rule is violated: "
                "**STOP and ask for human review.**"
            )

        return "\n".join(lines)

    def _render_capabilities(self, capabilities) -> str:
        if not capabilities:
            return ""

        lines = [
            "---",
            "alwaysApply: false",
            'description: "When using or invoking capabilities defined in the PGC governance contract"',
            "---",
            "",
            "# Capabilities",
            "",
            "| Capability | Owner | Description |",
            "|-----------|-------|-------------|",
        ]
        for c in capabilities:
            lines.append(f"| `{c.id}` | {c.owner_persona} | {c.description} |")
        return "\n".join(lines)
