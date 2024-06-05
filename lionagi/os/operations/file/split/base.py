from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from lionagi.files.util import Document


class BaseSplitter(ABC):
    def __init__(self, chunk_size: int, chunk_overlap: float):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def split_text(self, text: str) -> List[str]:
        """Abstract method to split text into multiple components."""

    def create_documents(
        self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[Document]:
        metadatas = metadatas or [{}] * len(texts)
        documents = []
        for i, text in enumerate(texts):
            for chunk in self.split_text(text):
                metadata = metadatas[i].copy()
                document = Document(content=chunk, metadata=metadata)
                documents.append(document)
        return documents
