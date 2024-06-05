from typing import List, Optional, Sequence, Any
from bs4 import BeautifulSoup, NavigableString
import logging

# Logger Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Utility Functions
def format_chunks(chunks: List[str], chunk_size: int) -> List[str]:
    merged_chunks = []
    current_chunk = []
    current_length = 0

    for chunk in chunks:
        chunk_length = len(chunk)
        if current_length + chunk_length > chunk_size:
            merged_chunks.append("".join(current_chunk))
            current_chunk = [chunk]
            current_length = chunk_length
        else:
            current_chunk.append(chunk)
            current_length += chunk_length + 1

    if current_chunk:
        merged_chunks.append("".join(current_chunk))

    return merged_chunks


def extract_text_from_tag(tag: Any, valid_tags: List[str]) -> str:
    texts = []
    for elem in tag.children:
        if isinstance(elem, NavigableString):
            if elem.strip():
                texts.append(elem.strip())
        elif elem.name in valid_tags:
            continue
        else:
            texts.append(elem.get_text().strip())
    return "\n".join(texts)


def build_node_from_split(
    text_split: str, node: Any, metadata: dict, include_metadata: bool
) -> Any:
    new_node = build_nodes_from_splits([text_split], node, id_func=node.id_func)[0]

    if include_metadata:
        new_node.metadata = {**new_node.metadata, **metadata}

    return new_node


# Base Classes
class BaseSplitter:
    def __init__(self, chunk_size: int, chunk_overlap: float):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap


class HTMLSplitter(BaseSplitter):
    def __init__(self, tag: str = "p", **kwargs):
        super().__init__(**kwargs)
        self.tag = tag

    def split_text(self, text: str) -> List[str]:
        soup = BeautifulSoup(text, "html.parser")
        elements = soup.find_all(self.tag)
        chunks = [str(element) for element in elements]
        return format_chunks(chunks, self.chunk_size)


class RecursiveHTMLSplitter(BaseSplitter):
    def __init__(self, tags: Optional[List[str]] = None, **kwargs):
        super().__init__(**kwargs)
        self.tags = tags or ["div", "p", "span", ""]

    def split_text(self, text: str) -> List[str]:
        soup = BeautifulSoup(text, "html.parser")
        return self._split_html(soup, self.tags)

    def _split_html(self, soup: BeautifulSoup, tags: List[str]) -> List[str]:
        final_chunks = []
        tag, new_tags = self._select_tag(soup, tags)
        elements = soup.find_all(tag) if tag else [soup]
        good_splits = []

        for elem in elements:
            text = elem.get_text()
            if len(text) < self.chunk_size:
                good_splits.append(text)
            else:
                if good_splits:
                    final_chunks.extend(format_chunks(good_splits, self.chunk_size))
                    good_splits = []
                if not new_tags:
                    final_chunks.append(text)
                else:
                    final_chunks.extend(
                        self._split_html(BeautifulSoup(text, "html.parser"), new_tags)
                    )

        if good_splits:
            final_chunks.extend(format_chunks(good_splits, self.chunk_size))
        return final_chunks

    def _select_tag(self, soup: BeautifulSoup, tags: List[str]) -> (str, List[str]):
        tag, new_tags = tags[-1], []
        for t in tags:
            if t == "":
                tag = t
                break
            if soup.find(t):
                tag = t
                new_tags = tags[tags.index(t) + 1 :]
                break
        return tag, new_tags


# Example usage
html_content = "<div><p>This is a long paragraph. " * 50 + "</p></div>" * 5
splitter = RecursiveHTMLSplitter(chunk_size=100, chunk_overlap=0.1)
documents = splitter.split_text(html_content)
