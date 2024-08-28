from pydantic import BaseModel, ConfigDict


class OpenAIBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        use_enum_values=True,
        json_schema_extra={"examples": []},
    )

    @classmethod
    def add_example(cls, example: dict):
        """Add an example to the model's JSON schema."""
        cls.model_config["json_schema_extra"]["examples"].append(example)

    class Config:
        allow_population_by_field_name = True
