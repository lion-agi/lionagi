from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import Field

from lionagi.tools.base import Prompt, Resource, ResourceCategory

here = Path(__file__).parent.resolve()

FRAMEWORK_PATH = "resources/frameworks"
FRAMEWORK_CHOICES = Literal["math", "optim", "custom_algebra"]


__all__ = (
    "SynthlangFramework",
    "SynthlangTemplate",
)


class SynthlangFramework(Resource):

    category: ResourceCategory = Field(
        default=ResourceCategory.FRAMEWORK, frozen=True
    )

    @classmethod
    def load_framework_options(cls) -> dict:
        import json

        fp = here / FRAMEWORK_PATH / "framework_options.json"
        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def load_from_template(
        cls, template: SynthlangTemplate | str
    ) -> SynthlangFramework:
        return SynthlangTemplate.load(template)

    @classmethod
    def load_base_system_prompt(cls) -> Prompt:
        fp = here / "resources/utility" / "base_synthlang_system_prompt.toml"
        return SynthlangFramework.adapt_from(fp, ".toml", many=False)

    @classmethod
    def build_framework_text(
        cls, framework_options: list[FRAMEWORK_CHOICES] = None
    ) -> str:
        FRAMEWORK_OPTIONS = cls.load_framework_options()
        lines = []
        if not framework_options:
            framework_options = FRAMEWORK_OPTIONS["options"].keys()

        for fw_key in framework_options:
            fw = FRAMEWORK_OPTIONS.get(fw_key, None)
            if fw:
                print(fw)
                lines.append(f"{fw['name']}: {fw['description']}")
                lines.append("Glyphs:")
                for g in fw["glyphs"]:
                    lines.append(
                        f"  {g['symbol']} -> {g['name']} ({g['description']})"
                    )
                lines.append("")
        return "\n".join(lines).strip()

    def create_system_prompt(
        self,
        framework_options: list[FRAMEWORK_CHOICES] = None,
        additional_text: str = "",
    ) -> str:

        framework_options_text = self.build_framework_text(framework_options)
        base_prompt = self.load_base_system_prompt()
        template_details = (
            f"Title: {self.meta_obj.title}\n"
            f"Domain: {str(self.meta_obj.domain)}\n"
            f"Category: {str(self.category)}\n"
            f"Overview: {self.meta_obj.overview}\n"
            "Excerpt:\n"
            f"{self.content}\n"
        )
        prompt = (
            f"{base_prompt.content}\n\n"
            "[Active Frameworks]\n"
            f"{framework_options_text}\n\n"
            "[Template]\n"
            f"{template_details}\n"
        )
        if additional_text.strip():
            prompt += f"\n[Additional]\n{additional_text.strip()}\n"

        return prompt.strip()


class SynthlangTemplate(str, Enum):
    ABSTRACT_ALGEBRA = "abstract_algebra"
    CATEGORY_THEORY = "category_theory"
    COMPLEX_ANALYSIS = "complex_analysis"
    GROUP_THEORY = "group_theory"
    MATH_LOGIC = "math_logic"
    REFLECTIVE_PATTERNS = "reflective_patterns"
    SET_THEORY = "set_theory"
    TOPOLOGY_FUNDAMENTALS = "topology_fundamentals"

    @property
    def fp(self) -> Path:
        return here / FRAMEWORK_PATH / f"{self.value}.toml"

    @classmethod
    def list_templates(cls) -> list[str]:
        return [template.value for template in cls]

    @classmethod
    def load(cls, framework: str) -> SynthlangFramework:
        framework = str(framework).strip().lower()
        framework = framework.replace(" ", "_").replace("-", "_")
        if ".toml" in framework:
            framework = framework.replace(".toml", "").strip()
        if "synthlangtemplate." in framework:
            framework = framework.replace("synthlangtemplate.", "").strip()
        try:
            framework = cls(framework)
        except ValueError:
            raise ValueError(f"Invalid synthlang framework name: {framework}")

        return SynthlangFramework.adapt_from(framework.fp, ".toml", many=False)
