import json
from typing import Any
from pathlib import Path
import pandas as pd

from lion_core.converter import ConverterRegistry, Converter


from lionagi.os.libs import to_dict
from lionagi.app.LlamaIndex.bridge import LlamaIndexBridge
from lionagi.app.LangChain.bridge import LangChainBridge


class NodeConverterRegistry(ConverterRegistry): ...


class JSONConverter(Converter):

    @staticmethod
    def from_obj(cls, obj: str | Path, **kwargs) -> dict:
        if isinstance(obj, str):
            obj = Path(obj)
        return json.load(open(obj))

    @staticmethod
    def to_obj(self, **kwargs) -> str:
        return json.dumps(to_dict(self), **kwargs)


class PandasSeriesConverter(Converter):

    @staticmethod
    def from_obj(cls, obj: pd.Series, **kwargs) -> dict:
        return to_dict(obj, **kwargs)

    @staticmethod
    def to_obj(self, **kwargs) -> pd.Series:
        return pd.Series(to_dict(self), **kwargs)


LLAMAINDEX_CONVERTER = LlamaIndexBridge.converter()
LANGCHAIN_CONVERTER = LangChainBridge.converter()

NodeConverterRegistry.register("json", JSONConverter)
NodeConverterRegistry.register("pandas_series", PandasSeriesConverter)
NodeConverterRegistry.register("llamaindex", LLAMAINDEX_CONVERTER)
NodeConverterRegistry.register("langchain", LANGCHAIN_CONVERTER)
