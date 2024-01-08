# use schema and convert_util
from ..utils.convert_util import func_to_schema
from ..schema.base_tool import Tool

def func_to_tool(func_, parser=None, docstring_style='google'):
    schema = func_to_schema(func_, docstring_style)
    return Tool(func=func_, parser=parser, schema_=schema)
