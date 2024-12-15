import pytest

from lionagi.libs.base import CodeBlock
from lionagi.libs.parse.extract_code_block import extract_code_block


def test_extract_single_code_block():
    markdown = """
Some text
```python
def hello():
    print("Hello, world!")
```
More text
"""
    result = extract_code_block(markdown)
    assert len(result) == 1
    assert isinstance(result[0], CodeBlock)
    assert result[0].lang == "python"
    assert result[0].code == 'def hello():\n    print("Hello, world!")\n'


def test_extract_multiple_code_blocks():
    markdown = """
```python
def hello():
    print("Hello")
```

```javascript
function hello() {
    console.log("Hello");
}
```
"""
    result = extract_code_block(markdown)
    assert len(result) == 2
    assert result[0].lang == "python"
    assert result[1].lang == "javascript"


def test_extract_with_tilde_fence():
    markdown = """
~~~python
def hello():
    print("Hello")
~~~
"""
    result = extract_code_block(markdown)
    assert len(result) == 1
    assert result[0].lang == "python"
    assert result[0].code == 'def hello():\n    print("Hello")\n'


def test_extract_without_language():
    markdown = """
```
plain text
```
"""
    result = extract_code_block(markdown)
    assert len(result) == 1
    assert result[0].lang == "plain"
    assert result[0].code == "plain text\n"


def test_extract_with_language_filter():
    markdown = """
```python
python code
```

```javascript
js code
```
"""
    result = extract_code_block(markdown, languages=["python"])
    assert len(result) == 1
    assert result[0].lang == "python"
    assert result[0].code == "python code\n"


def test_extract_categorized():
    markdown = """
```python
def hello():
    print("Hello")
```

```python
def world():
    print("World")
```

```javascript
console.log("Hello");
```
"""
    result = extract_code_block(markdown, categorize=True)
    assert isinstance(result, dict)
    assert len(result["python"]) == 2
    assert len(result["javascript"]) == 1
    assert all(
        isinstance(block, CodeBlock)
        for blocks in result.values()
        for block in blocks
    )


def test_extract_with_indented_fences():
    markdown = """
    ```python
    def hello():
        print("Hello")
    ```
"""
    result = extract_code_block(markdown)
    assert len(result) == 1
    assert result[0].lang == "python"


def test_extract_with_empty_code_block():
    markdown = """
```python
```
"""
    result = extract_code_block(markdown)
    assert len(result) == 1
    assert result[0].code == "\n"


def test_extract_with_no_code_blocks():
    markdown = "Just some text without any code blocks"
    result = extract_code_block(markdown)
    assert len(result) == 0


def test_extract_with_language_and_extra_spaces():
    markdown = """
```python   
def hello():
    print("Hello")
```
"""
    result = extract_code_block(markdown)
    assert len(result) == 1
    assert result[0].lang == "python"


def test_extract_with_language_filter_no_matches():
    markdown = """
```python
def hello():
    print("Hello")
```
"""
    result = extract_code_block(markdown, languages=["javascript"])
    assert len(result) == 0


def test_extract_categorized_with_language_filter():
    markdown = """
```python
python code
```

```javascript
js code
```

```python
more python code
```
"""
    result = extract_code_block(
        markdown, languages=["python"], categorize=True
    )
    assert isinstance(result, dict)
    assert len(result) == 1
    assert "python" in result
    assert len(result["python"]) == 2
    assert "javascript" not in result


def test_extract_with_special_characters():
    markdown = """
```python+django
from django.db import models
```
"""
    result = extract_code_block(markdown)
    assert len(result) == 1
    assert result[0].lang == "python+django"
