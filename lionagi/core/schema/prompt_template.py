from lionagi.libs import convert
from lionagi.core.schema.base_node import BaseComponent
from pydantic import BaseModel, Field


class PromptTemplate(BaseComponent):
    signature: str = Field("null", description="signature indicating inputs, outputs")

    def __init__(
        self,
        name_: str = "default_prompt_template",
        version_: str | float | int = None,
        description_: dict | str | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.metadata["prompt_name"] = name_
        self.metadata["version"] = version_
        self.metadata["description"] = description_ or ""

    @property
    def prompt_fields(self):
        return [
            _field
            for _field in self.property_keys
            if _field
            not in ["id_", "timestamp", "metadata", "prompt_fields", "signature"]
        ]

    @staticmethod
    def _get_input_output_fields(str_):
        _inputs, _outputs = str_.split("->")

        _inputs = [convert.strip_lower(i) for i in _inputs.split(",")]
        _outputs = [convert.strip_lower(o) for o in _outputs.split(",")]

        return _inputs, _outputs

    @property
    def input_fields(self):
        _inputs, _ = self._get_input_output_fields(self.signature)
        return _inputs

    @property
    def output_fields(self):
        _, _outputs = self._get_input_output_fields(self.signature)
        return _outputs

    def validate_field(self): ...

    def fix_field(self): ...

    def _to_instruction(self): ...


class Weather(PromptTemplate):
    sunny: bool = Field(
        True, description="true if the weather is sunny outside else false"
    )
    rainy: bool = Field(False, description="true if it is raining outside else false")
    play1: bool = Field(True, description="conduct play1")
    play2: bool = Field(False, description="conduct play2")
    signature: str = Field("sunny, rainy -> play1, play2")


a = Weather(name_="Weather", version_=1.0)
a.output_field  # ['play1', 'play2']
