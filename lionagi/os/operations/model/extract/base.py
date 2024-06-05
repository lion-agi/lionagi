from abc import ABC, abstractmethod
from typing import Any, Dict, List, Sequence

class BaseExtractor(ABC):
    @abstractmethod
    async def aextract(self, nodes: Sequence[Any]) -> List[Dict]:
        """Asynchronously extract metadata from nodes."""
        pass
