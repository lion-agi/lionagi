
# LionAGI Components Tutorial

## Introduction

This tutorial introduces the LionAGI components, focusing on the `Component` class and its various functionalities. LionAGI provides a flexible and extensible framework for defining and managing components, which are the building blocks for creating complex systems. This guide will cover the creation, manipulation, and usage of components within the LionAGI framework.

## Table of Contents

1. [Base Universal Attributes](#base-universal-attributes)
2. [Inherit from Component Class](#inherit-from-component-class)
3. [to_obj Methods](#to_obj-methods)
4. [from_obj Method](#from_obj-method)
5. [MetaData Manipulation](#metadata-manipulation)

## Base Universal Attributes

The `Component` class in LionAGI provides a set of base universal attributes that are common to all components. These attributes include a unique identifier, a timestamp, metadata, content, and more.

### Example Usage

The following code demonstrates the creation of a `Component` instance and prints its attributes.

```python
from lionagi.core.generic.abc.component import Component

# Create a Component instance
a = Component()
print(a)
# Output:
# ln_id         50a71430e3c42bd3c54e343d7143a072
# created             2024-05-14T02:06:49.220012
# metadata                                    {}
# content                                   None
# class_name                           Component
# dtype: object
```

### Setting Content

You can set the content of a component using the `content` attribute. This example sets the content to `1` and prints the component details.

```python
a.content = 1
a
# Output:
# ln_id                          50a71430e3c42bd3c54e343d7143a072
# created                              2024-05-14T02:06:49.220012
# metadata      {'last_updated': {'content': '2024-05-14T02:06...
# content                                                       1
# class_name                                            Component
# dtype: object
```

### Accessing Class Name

You can access the class name of the component using the `class_name` attribute.

```python
a.class_name
# Output: 'Component'
```

### Printing Attributes

The attributes of the component can be printed individually for clarity.

```python
print("ln_id: \t\t\t", a.ln_id)  # unique lion id
print("created at: \t\t", a.timestamp)
print("metadata: \t\t", a.metadata)
print("content: \t\t", a.content)
print("extra_fields: \t\t", a.extra_fields)
# Output:
# ln_id:              50a71430e3c42bd3c54e343d7143a072
# created at:          2024-05-14T02:06:49.220012
# metadata:          {'last_updated': {'content': '2024-05-14T02:06:49.225037'}}
# content:          1
# extra_fields:          {}
```

### Field Annotations

The `field_annotations` property provides information about the types and requirements of the fields.

```python
a._field_annotations
# Output:
# {'ln_id': ['str'],
#  'timestamp': ['str'],
#  'metadata': ['dict'],
#  'extra_fields': ['dict'],
#  'content': ['Any']}
```

### Field Information

The `_all_fields` attribute gives detailed information about each field, including its type, default value, and description.

```python
a._all_fields
# Output:
# {
#  'ln_id': FieldInfo(annotation=str, required=False, default_factory=create_id, alias_priority=2, validation_alias=AliasChoices(choices=['node_id', 'ID', 'id']), title='ID', description='A 32-char unique hash identifier.', frozen=True),
#  'timestamp': FieldInfo(annotation=str, required=False, default_factory=<lambda>, alias='created', alias_priority=2, validation_alias=AliasChoices(choices=['created_on', 'creation_date']), title='Creation Timestamp', description='The UTC timestamp of creation', frozen=True),
#  'metadata': FieldInfo(annotation=dict[str, Any], required=False, default_factory=dict, alias_priority=2, validation_alias=AliasChoices(choices=['meta', 'info']), description='Additional metadata for the component.'),
#  'extra_fields': FieldInfo(annotation=dict[str, Any], required=False, default_factory=dict, alias_priority=2, validation_alias=AliasChoices(choices=['extra', 'additional_fields', 'schema_extra', 'extra_schema']), description='Additional fields for the component.'),
#  'content': FieldInfo(annotation=Any, required=False, alias_priority=2, validation_alias=AliasChoices(choices=['text', 'page_content', 'chunk_content', 'data']), description='The optional content of the node.')
# }
```

## Inherit from Component Class

You can create custom components by inheriting from the `Component` class. This allows you to define additional fields and methods specific to your component.

### Example Usage

The following example demonstrates how to create a custom `Form` component by inheriting from the `Component` class.

```python
from pydantic import Field

class Form(Component):
    form_name: str = Field(default="form", title="Form Name")
    date: str = "today"

a = Form()
```

### Checking Field Attributes

You can check if a specific field has a particular attribute using the `_field_has_attr` method.

```python
a._field_has_attr("form_name", "title")
# Output: True
```

### Getting Field Attributes

You can get the value of a specific attribute of a field using the `_get_field_attr` method.

```python
a._get_field_attr("form_name", "title")
# Output: 'Form Name'
```

### Field Annotations for Custom Component

The `Form` component will have additional fields compared to the base `Component` class. You can view these annotations using the `_field_annotations` property.

```python
a._field_annotations
# Output:
# {'ln_id': ['str'],
#  'timestamp': ['str'],
#  'metadata': ['dict'],
#  'extra_fields': ['dict'],
#  'content': ['Any'],
#  'form_name': ['str'],
#  'date': ['str']}
```

### Adding a Field

You can dynamically add fields to a component using the `_add_field` method.

```python
a._add_field(
    field="welcome", annotation=str, default="new value", value="hello world again"
)
a._field_annotations
# Output:
# {'ln_id': ['str'],
#  'timestamp': ['str'],
#  'metadata': ['dict'],
#  'extra_fields': ['dict'],
#  'content': ['Any'],
#  'form_name': ['str'],
#  'date': ['str'],
#  'welcome': ['str']}
```

### Getting Field Values

You can get the default and current values of a dynamically added field.

```python
print("default value: \t", a._get_field_attr("welcome", "default", None))
print("current value: \t", getattr(a, "welcome", None))
# Output:
# default value:      new value
# current value:      hello world again
```

## to_obj Methods

The `to_obj` methods allow you to convert a component to different formats such as JSON, dictionary, XML, and pandas Series.

### JSON String

The `to_json_str` method converts the component to a JSON string.

```python
print("json_str: \n\n", a.to_json_str())
# Output:
# json_str: 
#
#  {"ln_id": "161d6169b07c7cfb527d3d2ec83893ff", "created": "2024-05-14T02:06:49.251951", "metadata": {"last_updated": {"welcome": "2024-05-14T02:06:49.280206"}}, "content": null, "form_name": "form", "date": "today", "welcome": "hello world again"}
```

### Dictionary

The `to_dict` method converts the component to a dictionary.

```python
print("dict: \n\n", a.to_dict())
# Output:
# dict: 
#
#  {'ln_id': '161d6169b07c7cfb527d3d2ec83893ff', 'created': '2024-05-14T02:06:49.251951', 'metadata': {'last_updated': {'welcome': '2024-05-14T02:06:49.280206'}}, 'content': None, 'form_name': 'form', 'date': 'today', 'welcome': 'hello world again'}
```

### XML

The `to_xml` method converts the component to an XML string.

```python
print("xml: \n\n", a.to_xml())
# Output:
# xml: 
#
#  <Form><ln_id>161d6169b07c7cfb527d3d2ec83893ff</ln_id><created>2024-05-14T02:06:49.251951</created><metadata><last_updated><welcome>2024-05-14T02:06:49.280206</welcome></last_updated></metadata><content>None</content><form_name>form</form_name><date>today</date><welcome>hello world again</welcome></Form

>
```

### Pandas Series

The `to_pd_series` method converts the component to a pandas Series.

```python
print("pd.Series: \n\n", a.to_pd_series())
# Output:
# pd.Series: 
#
#  ln_id                         161d6169b07c7cfb527d3d2ec83893ff
# created                             2024-05-14T02:06:49.251951
# metadata     {'last_updated': {'welcome': '2024-05-14T02:06...
# content                                                   None
# form_name                                                 form
# date                                                     today
# welcome                                      hello world again
# dtype: object
```

### LlamaIndex Node

The `to_llama_index_node` method converts the component to a LlamaIndex node.

```python
llama_node = a.to_llama_index_node()
type(llama_node)
# Output: llama_index.core.schema.TextNode
```

### LangChain Document

The `to_langchain_doc` method converts the component to a LangChain document.

```python
langchain_doc = a.to_langchain_doc()
type(langchain_doc)
# Output: langchain_core.documents.base.Document
```

## from_obj Method

The `from_obj` method allows you to create a component from various object types such as dictionaries, JSON strings, and pandas Series/DataFrames.

### Creating from Dictionary

You can create a component from a dictionary object.

```python
dict_obj = {"a": 1, "b": 2}
b = Component.from_obj(dict_obj)
b.to_dict()
# Output:
# {'ln_id': 'cb6b35ec0831ffdeb6a7f3a897a959e1',
#  'created': '2024-05-14T02:06:50.167285',
#  'metadata': {'a': 1, 'b': 2},
#  'content': None}
```

### Creating from JSON String

You can create a component from a JSON string.

```python
json_str_obj = '{"a": 1, "b": 2}'
a = Component.from_obj(json_str_obj)
a.to_dict()
# Output:
# {'ln_id': '71b94b77699186a6355424a210773e75',
#  'created': '2024-05-14T02:06:50.170624',
#  'metadata': {'a': 1, 'b': 2},
#  'content': None}
```

### Fuzzy Parsing JSON String

The `from_obj` method supports fuzzy parsing for incorrectly formatted JSON strings.

```python
json_str_obj = '{"name": "John", "age": 30, "city": ["New York", "DC", "LA"]'
a = Component.from_obj(json_str_obj, fuzzy_parse=True)
a.to_dict()
# Output:
# {'ln_id': '5f9f9aee20531f704e72ef0d9ee78439',
#  'created': '2024-05-14T02:06:50.174160',
#  'metadata': {'name': 'John', 'age': 30, 'city': ['New York', 'DC', 'LA']},
#  'content': None}
```

### Creating from Pandas Series

You can create a component from a pandas Series object.

```python
import pandas as pd

series_obj = pd.Series({"a": 1, "b": 2})
a = Component.from_obj(series_obj)
a.to_dict()
# Output:
# {'ln_id': '9b07d72487f54a3cfbdcd976b47c8cb3',
#  'created': '2024-05-14T02:06:50.177804',
#  'metadata': {'a': 1, 'b': 2},
#  'content': None}
```

### Creating from Pandas DataFrame

When you create a component object from a DataFrame, the output will be a list of component objects.

```python
df = pd.DataFrame({"a": [1, 2], "b": [3, 4]}, index=["row1", "row2"])
a = Component.from_obj(df)
type(a)
# Output: list

for i in a:
    print(i.to_dict())
# Output:
# {'ln_id': '05b6addf5371d0847e05d2742fcf6e15', 'created': '2024-05-14T02:06:50.191905', 'metadata': {'a': 1, 'b': 3}, 'content': None}
# {'ln_id': 'c8e79bcdb5ff6e95d61271e4d35d6317', 'created': '2024-05-14T02:06:50.191971', 'metadata': {'a': 2, 'b': 4}, 'content': None}
```

## MetaData Manipulation

LionAGI allows for flexible manipulation of metadata within components. Metadata can be modified using specific methods to ensure data integrity.

### Getting Metadata

You can retrieve metadata using the `metadata` attribute.

```python
a.metadata
# Output:
# {'langchain': 1,
#  'lc_type': 'constructor',
#  'lc_id': ['langchain', 'schema', 'document', 'Document'],
#  'last_updated': {'welcome': '2024-05-14T02:06:50.230920'}}
```

### Setting Metadata

Directly setting the metadata attribute is not recommended as it might lose information or cause unexpected behavior. Instead, use `_meta_insert` or `_meta_set` methods.

```python
a._meta_insert("new_key2", "new_value2")
a._meta_set("langchain", 5)

a.metadata
# Output:
# {'langchain': 5,
#  'lc_type': 'constructor',
#  'lc_id': ['langchain', 'schema', 'document', 'Document'],
#  'last_updated': {'welcome': '2024-05-14T02:06:50.230920'},
#  'new_key2': 'new_value2'}
```

### Nested Metadata

The `_meta_insert` method supports nested data structures for more complex metadata management.

```python
a._meta_insert(["nested", 0], {"a": 1, "b": 2})
a.metadata
# Output:
# {'langchain': 5,
#  'lc_type': 'constructor',
#  'lc_id': ['langchain', 'schema', 'document', 'Document'],
#  'last_updated': {'welcome': '2024-05-14T02:06:50.230920'},
#  'new_key2': 'new_value2',
#  'nested': [{'a': 1, 'b': 2}]}
```

### Retrieving Nested Metadata

You can get a deeply nested value from metadata using the `_meta_get` method.

```python
a._meta_get(["nested", 0, "a"])
# Output: 1
```

This concludes the tutorial on LionAGI components. By understanding these fundamental operations, you can effectively create and manage components within the LionAGI framework.
