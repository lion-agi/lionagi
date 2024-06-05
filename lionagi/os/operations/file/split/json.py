import json
from typing import List, Dict, Any, Optional


class JSONChunker:
    def __init__(self, chunk_size: int, chunk_overlap: float):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        data = json.loads(text)
        chunks = self._split_json(data)
        return [json.dumps(chunk) for chunk in chunks]

    def _split_json(
        self,
        data: Dict[str, Any],
        current_path: Optional[List[str]] = None,
        chunks: Optional[List[Dict]] = None,
    ) -> List[Dict]:
        current_path = current_path or []
        chunks = chunks or [{}]
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = current_path + [key]
                chunk_size = len(json.dumps(chunks[-1]))
                size = len(json.dumps({key: value}))
                remaining = self.chunk_size - chunk_size

                if size < remaining:
                    self._set_nested_dict(chunks[-1], new_path, value)
                else:
                    if chunk_size >= self.chunk_size * (1 - self.chunk_overlap):
                        chunks.append({})

                    self._split_json(value, new_path, chunks)
        else:
            self._set_nested_dict(chunks[-1], current_path, data)
        return chunks

    def _set_nested_dict(self, d: Dict, path: List[str], value: Any) -> None:
        for key in path[:-1]:
            d = d.setdefault(key, {})
        d[path[-1]] = value


# Example usage
json_content = '{"a": 1, "b": {"c": 2, "d": {"e": 3, "f": 4}}}'
splitter = JSONChunker(chunk_size=50, chunk_overlap=0.1)
documents = splitter.split_text(json_content)


class RecursiveJSONChunker(JSONChunker):
    def __init__(self, chunk_size: int, chunk_overlap: float):
        super().__init__(chunk_size, chunk_overlap)

    def _split_json(
        self,
        data: Any,
        current_path: Optional[List[str]] = None,
        chunks: Optional[List[Dict]] = None,
    ) -> List[Dict]:
        current_path = current_path or []
        chunks = chunks or [{}]
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = current_path + [key]
                chunk_size = len(json.dumps(chunks[-1]))
                size = len(json.dumps({key: value}))
                remaining = self.chunk_size - chunk_size

                if size < remaining:
                    self._set_nested_dict(chunks[-1], new_path, value)
                else:
                    if chunk_size >= self.chunk_size * (1 - self.chunk_overlap):
                        chunks.append({})

                    self._split_json(value, new_path, chunks)
        else:
            self._set_nested_dict(chunks[-1], current_path, data)
        return chunks


# Example usage
json_content = '{"a": 1, "b": {"c": 2, "d": {"e": 3, "f": 4}}}'
splitter = RecursiveJSONChunker(chunk_size=50, chunk_overlap=0.1)
documents = splitter.split_text(json_content)
