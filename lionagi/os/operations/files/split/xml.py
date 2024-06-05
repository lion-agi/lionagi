from xml.etree import ElementTree as ET
from typing import List
from .base import BaseSplitter


class RecursiveXMLSplitter(BaseSplitter):
    def __init__(self, tags: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.tags = tags or ["section", "subsection", "paragraph", ""]

    def _split_xml(self, element: ET.Element, tags: List[str]) -> List[str]:
        final_chunks = []
        tag = tags[-1]
        new_tags = []
        for t in tags:
            if t == "":
                tag = t
                break
            if element.find(t):
                tag = t
                new_tags = tags[tags.index(t) + 1 :]
                break

        elements = element.findall(tag) if tag else [element]
        good_splits = []
        for elem in elements:
            text = ET.tostring(elem, encoding="unicode")
            if len(text) < self.chunk_size:
                good_splits.append(text)
            else:
                if good_splits:
                    final_chunks.extend(self._merge_splits(good_splits))
                    good_splits = []
                if not new_tags:
                    final_chunks.append(text)
                else:
                    final_chunks.extend(self._split_xml(elem, new_tags))
        if good_splits:
            final_chunks.extend(self._merge_splits(good_splits))
        return final_chunks

    def split_text(self, text: str) -> List[str]:
        root = ET.fromstring(text)
        return self._split_xml(root, self.tags)

    def _merge_splits(self, splits: List[str]) -> List[str]:
        merged_splits = []
        current_chunk = []
        current_length = 0

        for split in splits:
            split_length = len(split)
            if current_length + split_length > self.chunk_size:
                merged_splits.append("".join(current_chunk))
                current_chunk = [split]
                current_length = split_length
            else:
                current_chunk.append(split)
                current_length += split_length + 1

        if current_chunk:
            merged_splits.append("".join(current_chunk))

        return merged_splits


# Example usage
xml_content = """
<root>
  <section>
    <title>Section 1</title>
    <paragraph>This is a paragraph in section 1.</paragraph>
  </section>
  <section>
    <title>Section 2</title>
    <paragraph>This is a paragraph in section 2.</paragraph>
  </section>
</root>
"""
splitter = RecursiveXMLSplitter(chunk_size=100, chunk_overlap=0.1)
documents = splitter.create_documents([xml_content])
