from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import Field

from lionagi.tools.base import Resource, ResourceCategory

here = Path(__file__).parent.resolve()
MAPPING_PATH = "synthlang_/resources/mapping"


class TokenMappingTemplate(str, Enum):
    RUST_CHINESE = "rust_chinese"
    LION_EMOJI = "lion_emoji"

    @property
    def fp(self) -> Path:
        return here / MAPPING_PATH / f"{self.value}_mapping.toml"


class TokenMapping(Resource):
    category: ResourceCategory = Field(
        default=ResourceCategory.UTILITY, frozen=True
    )
    content: dict

    @classmethod
    def load_from_template(
        cls, template: TokenMappingTemplate | str
    ) -> TokenMapping:
        if isinstance(template, str):
            template = template.lower().strip()
            template = (
                template.replace(".toml", "")
                .replace(" ", "_")
                .replace("-", "_")
                .strip()
            )
            if template.endswith("_mapping"):
                template = template[:-8]
            if "/" in template:
                template = template.split("/")[-1]
            template = TokenMappingTemplate(template)

        if isinstance(template, TokenMappingTemplate):
            template = template.fp
            return cls.adapt_from(template, ".toml", many=False)

        raise ValueError(
            f"Invalid template: {template}. Must be a TokenMappingTemplate or a valid path."
        )
