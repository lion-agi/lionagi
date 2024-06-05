from typing import Any, Callable, List, Optional, Sequence, TypedDict

import numpy as np
import nltk

nltk.download("punkt")

DEFAULT_OG_TEXT_METADATA_KEY = "original_text"


class SentenceCombination(TypedDict):
    sentence: str
    index: int
    combined_sentence: str
    combined_sentence_embedding: List[float]


class SemanticSplitterNodeParser:
    """Semantic node parser.

    Splits a document into nodes, with each node being a group of semantically related sentences.

    Args:
        buffer_size (int): number of sentences to group together when evaluating semantic similarity
        embed_model: (BaseEmbedding): embedding model to use
        sentence_splitter (Optional[Callable]): splits text into sentences
        include_metadata (bool): whether to include metadata in nodes
        include_prev_next_rel (bool): whether to include prev/next relationships
    """

    def __init__(
        self,
        embed_model: Callable,
        buffer_size: int = 1,
        sentence_splitter: Optional[Callable[[str], List[str]]] = None,
        breakpoint_percentile_threshold: int = 95,
        include_metadata: bool = True,
        include_prev_next_rel: bool = True,
    ):
        self.embed_model = embed_model
        self.buffer_size = buffer_size
        self.sentence_splitter = sentence_splitter or nltk.sent_tokenize
        self.breakpoint_percentile_threshold = breakpoint_percentile_threshold
        self.include_metadata = include_metadata
        self.include_prev_next_rel = include_prev_next_rel

    def split_text(self, text: str) -> List[str]:
        sentences = self.sentence_splitter(text)
        sentences = self._build_sentence_groups(sentences)

        combined_sentence_embeddings = self.embed_model.get_text_embedding_batch(
            [s["combined_sentence"] for s in sentences]
        )

        for i, embedding in enumerate(combined_sentence_embeddings):
            sentences[i]["combined_sentence_embedding"] = embedding

        distances = self._calculate_distances_between_sentence_groups(sentences)

        chunks = self._build_node_chunks(sentences, distances)
        return chunks

    def _build_sentence_groups(
        self, text_splits: List[str]
    ) -> List[SentenceCombination]:
        sentences: List[SentenceCombination] = [
            {
                "sentence": x,
                "index": i,
                "combined_sentence": "",
                "combined_sentence_embedding": [],
            }
            for i, x in enumerate(text_splits)
        ]

        for i in range(len(sentences)):
            combined_sentence = ""

            for j in range(i - self.buffer_size, i):
                if j >= 0:
                    combined_sentence += sentences[j]["sentence"]

            combined_sentence += sentences[i]["sentence"]

            for j in range(i + 1, i + 1 + self.buffer_size):
                if j < len(sentences):
                    combined_sentence += sentences[j]["sentence"]

            sentences[i]["combined_sentence"] = combined_sentence

        return sentences

    def _calculate_distances_between_sentence_groups(
        self, sentences: List[SentenceCombination]
    ) -> List[float]:
        distances = []
        for i in range(len(sentences) - 1):
            embedding_current = sentences[i]["combined_sentence_embedding"]
            embedding_next = sentences[i + 1]["combined_sentence_embedding"]

            similarity = self.embed_model.similarity(embedding_current, embedding_next)
            distance = 1 - similarity
            distances.append(distance)

        return distances

    def _build_node_chunks(
        self, sentences: List[SentenceCombination], distances: List[float]
    ) -> List[str]:
        chunks = []
        if distances:
            breakpoint_distance_threshold = np.percentile(
                distances, self.breakpoint_percentile_threshold
            )

            indices_above_threshold = [
                i for i, x in enumerate(distances) if x > breakpoint_distance_threshold
            ]

            start_index = 0

            for index in indices_above_threshold:
                group = sentences[start_index : index + 1]
                combined_text = "".join([d["sentence"] for d in group])
                chunks.append(combined_text)
                start_index = index + 1

            if start_index < len(sentences):
                combined_text = "".join(
                    [d["sentence"] for d in sentences[start_index:]]
                )
                chunks.append(combined_text)
        else:
            chunks = [" ".join([s["sentence"] for s in sentences])]

        return chunks

    def create_documents(self, texts: List[str]) -> List[List[str]]:
        documents = [self.split_text(text) for text in texts]
        return documents
