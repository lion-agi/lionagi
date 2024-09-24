from pydantic import BaseModel
from lionagi.core.manual.guide import OperationGuide


class OperationManual(BaseModel):
    name: str
    version: str
    guides: list[OperationGuide] = []
    metadata: dict = {}
