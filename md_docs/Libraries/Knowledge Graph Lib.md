# Knowledge Base Utility API Reference

This module provides classes and methods for managing a Knowledge Base (KB) containing entities, relations, and sources. It also includes functionality for extracting knowledge graph triplets from text using pre-trained models.

## Classes

### `KnowledgeBase`

A class to represent a Knowledge Base (KB) containing entities, relations, and sources.

#### Attributes:
- `entities` (`dict`): A dictionary of entities in the KB, where the keys are entity titles, and the values are entity information (excluding the title).
- `relations` (`list`): A list of relations in the KB, where each relation is a dictionary containing information about the relation (head, type, tail) and metadata (article_url and spans).
- `sources` (`dict`): A dictionary of information about the sources of relations, where the keys are article URLs, and the values are source data (article_title and article_publish_date).

#### Methods:

#### `__init__()`
Initialize an empty Knowledge Base (KB) with empty dictionaries for entities, relations, and sources.

```python
def __init__():
```

#### `merge_with_kb(kb2)`
Merge another Knowledge Base (KB) into this KB.

```python
def merge_with_kb(kb2: KnowledgeBase):
```

**Parameters**:
- `kb2` (`KnowledgeBase`): The Knowledge Base (KB) to merge into this KB.

#### `are_relations_equal(r1, r2)`
Check if two relations (r1 and r2) are equal.

```python
def are_relations_equal(r1: dict, r2: dict) -> bool:
```

**Parameters**:
- `r1` (`dict`): The first relation to compare.
- `r2` (`dict`): The second relation to compare.

**Returns**:
- `bool`: True if the relations are equal, False otherwise.

#### `exists_relation(r1)`
Check if a relation (r1) already exists in the KB.

```python
def exists_relation(r1: dict) -> bool:
```

**Parameters**:
- `r1` (`dict`): The relation to check for existence in the KB.

**Returns**:
- `bool`: True if the relation exists in the KB, False otherwise.

#### `merge_relations(r2)`
Merge the information from relation r2 into an existing relation in the KB.

```python
def merge_relations(r2: dict):
```

**Parameters**:
- `r2` (`dict`): The relation to merge into an existing relation in the KB.

#### `get_wikipedia_data(candidate_entity)`
Get data for a candidate entity from Wikipedia.

```python
@cd.cache(maxsize=10000)
def get_wikipedia_data(candidate_entity: str) -> dict:
```

**Parameters**:
- `candidate_entity` (`str`): The candidate entity title.

**Returns**:
- `dict`: A dictionary containing information about the candidate entity (title, url, summary). None if the entity does not exist in Wikipedia.

#### `add_entity(e)`
Add an entity to the KB.

```python
def add_entity(e: dict):
```

**Parameters**:
- `e` (`dict`): A dictionary containing information about the entity (title and additional attributes).

#### `add_relation(r, article_title, article_publish_date)`
Add a relation to the KB.

```python
def add_relation(r: dict, article_title: str, article_publish_date: str):
```

**Parameters**:
- `r` (`dict`): A dictionary containing information about the relation (head, type, tail, and metadata).
- `article_title` (`str`): The title of the article containing the relation.
- `article_publish_date` (`str`): The publish date of the article.

#### `print()`
Print the entities, relations, and sources in the KB.

```python
def print():
```

#### `extract_relations_from_model_output(text)`
Extract relations from the model output text.

```python
@staticmethod
def extract_relations_from_model_output(text: str) -> list:
```

**Parameters**:
- `text` (`str`): The model output text containing relations.

**Returns**:
- `list`: A list of dictionaries, where each dictionary represents a relation (head, type, tail).

### `KGTripletExtractor`

A class to perform knowledge graph triplet extraction from text using a pre-trained model.

#### Methods:

#### `text_to_wiki_kb(text, model=None, tokenizer=None, device='cpu', span_length=512, article_title=None, article_publish_date=None, verbose=False)`
Extract knowledge graph triplets from text and create a Knowledge Base (KB) containing entities and relations.

```python
@staticmethod
def text_to_wiki_kb(
    text: str,
    model: Optional[AutoModelForSeq2SeqLM] = None,
    tokenizer: Optional[AutoTokenizer] = None,
    device: str = "cpu",
    span_length: int = 512,
    article_title: Optional[str] = None,
    article_publish_date: Optional[str] = None,
    verbose: bool = False
) -> KnowledgeBase:
```

**Parameters**:
- `text` (`str`): The input text from which triplets will be extracted.
- `model` (`AutoModelForSeq2SeqLM`, optional): The pre-trained model for triplet extraction. Defaults to None.
- `tokenizer` (`AutoTokenizer`, optional): The tokenizer for the model. Defaults to None.
- `device` (`str`, optional): The device to run the model on (e.g., 'cpu', 'cuda'). Defaults to 'cpu'.
- `span_length` (`int`, optional): The maximum span length for input text segmentation. Defaults to 512.
- `article_title` (`str`, optional): The title of the article containing the input text. Defaults to None.
- `article_publish_date` (`str`, optional): The publish date of the article. Defaults to None.
- `verbose` (`bool`, optional): Whether to enable verbose mode for debugging. Defaults to False.

**Returns**:
- `KnowledgeBase`: A Knowledge Base (KB) containing extracted entities, relations, and sources.

### `KGraph`

A class representing a Knowledge Graph (KGraph) for extracting relations from text.

#### Methods:

#### `text_to_wiki_kb(text, **kwargs)`
Extract relations from input text and create a Knowledge Base (KB) containing entities and relations.

```python
@staticmethod
def text_to_wiki_kb(text: str, **kwargs) -> KnowledgeBase:
```

**Parameters**:
- `text` (`str`): The input text from which relations are extracted.
- `**kwargs`: Additional keyword arguments passed to the underlying extraction method.

**Returns**:
- `KnowledgeBase`: A Knowledge Base (KB) containing entities and relations extracted from the input text.

## Usage Examples

```python
from lionagi.libs.knowledge_base import KnowledgeBase, KGTripletExtractor, KGraph

# Initialize a Knowledge Base
kb = KnowledgeBase()

# Add entities and relations
entity = {"title": "Albert Einstein", "url": "https://en.wikipedia.org/wiki/Albert_Einstein", "summary": "Albert Einstein was a theoretical physicist."}
kb.add_entity(entity)

relation = {
    "head": "Albert Einstein",
    "type": "born_in",
    "tail": "Ulm",
    "meta": {"https://en.wikipedia.org/wiki/Albert_Einstein": {"spans": [(0, 50)]}}
}
kb.add_relation(relation, article_title="Albert Einstein", article_publish_date="2023-01-01")

# Merge another KB
kb2 = KnowledgeBase()
kb2.add_entity({"title": "Niels Bohr", "url": "https://en.wikipedia.org/wiki/Niels_Bohr", "summary": "Niels Bohr was a Danish physicist."})
relation2 = {
    "head": "Niels Bohr",
    "type": "collaborated_with",
    "tail": "Albert Einstein",
    "meta": {"https://en.wikipedia.org/wiki/Niels_Bohr": {"spans": [(51, 100)]}}
}
kb2.add_relation(relation2, article_title="Niels Bohr", article_publish_date="2023-02-01")
kb.merge_with_kb(kb2)

# Print KB contents
kb.print()

# Extract triplets from text
text = "Albert Einstein was born in Ulm. He collaborated with Niels Bohr."
kb_extracted = KGTripletExtractor.text_to_wiki_kb(text, verbose=True)
kb_extracted.print()

# Use KGraph to extract triplets
kb_extracted_kgraph = KGraph.text_to_wiki_kb(text, verbose=True)
kb_extracted_kgraph.print()
```

These examples demonstrate how to use the various classes and methods provided by the `KnowledgeBase`, `KGTripletExtractor`, and `KGraph` classes in `ln_knowledge_graph`. You can initialize a Knowledge Base, add entities and relations, merge multiple Knowledge Bases, and extract knowledge graph triplets from text using pre-trained models.
