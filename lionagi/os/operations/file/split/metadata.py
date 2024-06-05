from typing import List, Dict, Any


class MetadataSplitter(BaseSplitter):
    def __init__(self, metadata_key: str, **kwargs):
        super().__init__(**kwargs)
        self.metadata_key = metadata_key

    def split_text(self, text: str, metadata: List[Dict[str, Any]]) -> List[str]:
        chunks = []
        current_chunk = []
        current_length = 0

        for i, segment in enumerate(text.split()):
            segment_length = len(segment)
            if current_length + segment_length > self.chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [segment]
                current_length = segment_length
            else:
                current_chunk.append(segment)
                current_length += segment_length + 1

            if i < len(metadata) and self.metadata_key in metadata[i]:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_length = 0

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks


# Example usage
text_content = "Log entry one. Log entry two. Log entry three."
metadata = [
    {"timestamp": "2021-01-01"},
    {"timestamp": "2021-01-02"},
    {"timestamp": "2021-01-03"},
]
splitter = MetadataSplitter(metadata_key="timestamp", chunk_size=50, chunk_overlap=0.1)
documents = splitter.create_documents([text_content], metadata=metadata)
