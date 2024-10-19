from pydantic import BaseModel, Field

from .idea import IdeaModel


class BrainstormModel(BaseModel):
    topic: str = Field(
        ...,
        description="**Specify the topic or theme for the brainstorming session.**",
    )
    ideas: list[IdeaModel] = Field(
        default_factory=list,
        description="**Provide a list of ideas as `IdeaModel` instances. Each should contain a concise description of the idea.**",
    )
