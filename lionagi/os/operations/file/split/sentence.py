import nltk
from typing import List, Callable, Optional

nltk.download("punkt")


class SentenceSplitter:
    def __init__(
        self, chunk_size: int = 100, chunk_overlap: int = 10, language: str = "english"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.language = language

    def split_text(self, text: str) -> List[str]:
        sentences = nltk.sent_tokenize(text, language=self.language)
        return self._merge_splits(sentences)

    def _merge_splits(self, splits: List[str]) -> List[str]:
        merged_splits = []
        current_chunk = []
        current_length = 0

        for split in splits:
            split_length = len(split)
            if current_length + split_length > self.chunk_size:
                merged_splits.append(" ".join(current_chunk))
                current_chunk = [split]
                current_length = split_length
            else:
                current_chunk.append(split)
                current_length += split_length + 1

        if current_chunk:
            merged_splits.append(" ".join(current_chunk))

        return merged_splits

    def create_documents(self, texts: List[str]) -> List[List[str]]:
        documents = [self.split_text(text) for text in texts]
        return documents


class SBDSplitter:
    def __init__(
        self,
        chunk_size: int = 100,
        chunk_overlap: int = 10,
        language_model: str = "en_core_web_sm",
    ):
        import spacy

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.nlp = spacy.load(language_model)

    def split_text(self, text: str) -> List[str]:
        doc = self.nlp(text)
        sentences = [sent.text for sent in doc.sents]
        return self._merge_splits(sentences)

    def _merge_splits(self, splits: List[str]) -> List[str]:
        merged_splits = []
        current_chunk = []
        current_length = 0

        for split in splits:
            split_length = len(split)
            if current_length + split_length > self.chunk_size:
                merged_splits.append(" ".join(current_chunk))
                current_chunk = [split]
                current_length = split_length
            else:
                current_chunk.append(split)
                current_length += split_length + 1

        if current_chunk:
            merged_splits.append(" ".join(current_chunk))

        return merged_splits

    def create_documents(self, texts: List[str]) -> List[List[str]]:
        documents = [self.split_text(text) for text in texts]
        return documents


class SentenceWindowNodeParser:
    def __init__(
        self,
        window_size: int = 3,
        chunk_size: int = 100,
        chunk_overlap: int = 10,
        language: str = "english",
    ):
        self.window_size = window_size
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.language = language

    def split_text(self, text: str) -> List[str]:
        sentences = nltk.sent_tokenize(text, language=self.language)
        return sentences

    def build_window_nodes(self, text: str) -> List[dict]:
        sentences = self.split_text(text)
        nodes = []

        for i, sentence in enumerate(sentences):
            window_start = max(0, i - self.window_size)
            window_end = min(len(sentences), i + self.window_size + 1)
            window = sentences[window_start:window_end]
            node = {
                "sentence": sentence,
                "window": window,
                "metadata": {
                    "original_text": sentence,
                    "window_text": " ".join(window),
                },
            }
            nodes.append(node)

        return nodes

    def create_documents(self, texts: List[str]) -> List[List[dict]]:
        documents = [self.build_window_nodes(text) for text in texts]
        return documents
