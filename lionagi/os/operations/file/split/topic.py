from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation


class TopicSplitter(BaseSplitter):
    def __init__(self, n_topics: int = 5, **kwargs):
        super().__init__(**kwargs)
        self.n_topics = n_topics
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.lda_model = LatentDirichletAllocation(n_components=self.n_topics)

    def split_text(self, text: str) -> List[str]:
        sentences = text.split(". ")
        tfidf_matrix = self.vectorizer.fit_transform(sentences)
        lda_matrix = self.lda_model.fit_transform(tfidf_matrix)
        topics = lda_matrix.argmax(axis=1)

        chunks = []
        current_chunk = []
        current_topic = topics[0]

        for i, sentence in enumerate(sentences):
            if (
                topics[i] != current_topic
                or len(" ".join(current_chunk)) > self.chunk_size
            ):
                chunks.append(". ".join(current_chunk) + ".")
                current_chunk = [sentence]
                current_topic = topics[i]
            else:
                current_chunk.append(sentence)

        if current_chunk:
            chunks.append(". ".join(current_chunk) + ".")

        return chunks


# Example usage
text_content = "Topic one sentence one. Topic one sentence two. Topic two sentence one. Topic two sentence two."
splitter = TopicSplitter(chunk_size=50, chunk_overlap=0.1)
documents = splitter.create_documents([text_content])
