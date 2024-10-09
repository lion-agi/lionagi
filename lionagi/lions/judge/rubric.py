from pydantic import BaseModel


class RubricItem(BaseModel):
    name: str
    prompt: str
    description: str | None = None
    weight: float | int = 1
    metadata: dict = {}


class Rubric(BaseModel):
    name: str
    description: str
    items: dict[str, RubricItem]
    metadata: dict = {}

    @property
    def analysis_types(self):
        return list(self.items.keys())

    @property
    def normalized_weight(self):
        return {
            item.name: item.weight / self.ttl_weights
            for item in self.items.values()
        }

    @property
    def ttl_weights(self):
        return sum([item.weight for item in self.items.values()])


__all__ = ["Rubric", "RubricItem"]
