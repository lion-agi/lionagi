from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from lionagi.protocols.graph.node import Node


class DocInfo(BaseModel):

    @property
    def suffix(self) -> str:
        if self.file_path is None:
            return None

        fp = Path(self.file_path)
        if fp.exists() and fp.is_file():
            return Path(self.file_path).suffix
        return None


class Document(Node):

    pass
