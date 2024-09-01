from lion_core import LN_UNDEFINED
from ._converters.json_converter import JSONStringConverter, JSONFileConverter
from ._converters.xml_converter import XMLStringConverter, XMLFileConverter
from ._converters.pydantic_converter import DynamicPydanticConverter, DynamicLionModelConverter
from lionagi.app.LlamaIndex.bridge import LlamaIndexBridge
from lionagi.app.LangChain.bridge import LangChainBridge
from lionagi.app.Pandas.convert import PandasSeriesConverter

from .utils import validate_embedding

from lionagi.os import lionfuncs as ln


llamaindex_converter = LlamaIndexBridge.converter()
langchain_converter = LangChainBridge.converter()


def process_generic_dict(dict_: dict) -> dict:
    """Process a generic dictionary."""
    
    # if there are lion_class key we assume the dictionary is originally 
    # from a lion object
    if "lion_class" in dict_ and SysUtil.is_id(dict_.get("metadata", {}).get("ln_id", {})):
        return dict_
    
    metadata = ln.to_dict(dict_.pop("metadata", {}))
    metadata.update(ln.to_dict(dict_.pop("meta", {})))
    
    if "ln_id" not in dict_ and "ln_id" in metadata:
        dict_["ln_id"] = metadata.pop("ln_id")
    if "timestamp" not in dict_ and "timestamp" in metadata:
        dict_["timestamp"] = metadata.pop("timestamp")
        
    if "ln_id" in dict_:
        dict_["metadata"] = metadata
        return dict_
    
    dict_["metadata"] = {"extra_meta": metadata}
    dict_["content"] = dict_.pop("content", LN_UNDEFINED)

    if dict_["content"] is LN_UNDEFINED:
        for field in ["page_content", "text", "chunk_content", "data"]:
            if field in dict_:
                dict_["content"] = dict_.pop(field)
                break
            
    return dict_


def dispatch_from_dict(cls: Component, obj: dict) -> dict:
    
    kind_ = None
        
    if "embedding" in obj:
        obj["embedding"] = validate_embedding(obj["embedding"])
    
    
    
    
    
    
    
    
    
    
    
    
    
    if "lc" in obj:
        return langchain_converter.



    return process_generic_dict(obj)

    
    
    
    
    
    
    
    
    
    
    
    



def _node_from_dict_dispatch(cls: Component, obj: dict, **kwargs):
    dict_ = {**obj, **kwargs}
    kind_ = None
    
    if "embedding" in dict_:
        dict_["embedding"] = validate_embedding(dict_["embedding"])


    
    elif 




    if "lc" in dict_:  # LangChain
        return LangChainBridge.from_dict(dict_)

    try:

        if "embedding" in dict_:
            dict_["embedding"] = cls._validate_embedding(dict_["embedding"])

        if "lion_class" in dict_:
            cls = _init_class.get(dict_.pop("lion_class"), cls)

        if "lc" in dict_:
            dict_ = cls._process_langchain_dict(dict_)
        else:
            dict_ = cls._process_generic_dict(dict_)

        return cls.model_validate(dict_, *args, **kwargs)

    except ValidationError as e:
        raise LionValueError("Invalid dictionary for deserialization.") from e

















import contextlib
import os
import json
from typing import Any
from pathlib import Path
import pandas as pd
from pydantic import BaseModel, create_model
from lion_core.converter import ConverterRegistry, Converter
from lion_core.generic.component import Component

from lionagi.os.libs import to_dict
from lionagi.os.sys_utils import SysUtil









class NodeConverterRegistry(ConverterRegistry):
    pass


converters = {
    "json": JSONStringConverter,
    "pd_series": PandasSeriesConverter,
    "xml": XMLStringConverter,
    "dynamic_base_model": DynamicPydanticConverter,
    "dynamic_lion_model": DynamicLionModelConverter,
    "llamaindex": LlamaIndexBridge.converter(),
    "langchain": LangChainBridge.converter(),
}

for k, v in converters.items():
    NodeConverterRegistry.register(k, v)





__all__ = ["NodeConverterRegistry"]
