from pydantic import BaseModel, Field


class IdeaModel(BaseModel):
    content: str = Field(
        ...,
        description="**Provide a concise and clear description of the idea.**",
    )
