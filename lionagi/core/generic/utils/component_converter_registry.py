from lion_core.converter import ConverterRegistry
from lionagi.integrations.bridge.langchain_.converter import LangChainConverter

from .json_converter import JsonStringConverter, JsonFileConverter
from .pandas_converter import PandasSeriesConverter
from .xml_converter import XMLStringConverter, XMLFileConverter
from .pydantic_converter import DynamicPydanticConverter, DynamicLionModelConverter


class ComponentConverterRegistry(ConverterRegistry):
    _converters = {
        "dynamic_pydantic": DynamicPydanticConverter,
        "dynamic_lion": DynamicLionModelConverter,
        "pd_series": PandasSeriesConverter,
        "json": JsonStringConverter,
        "json_file": JsonFileConverter,
        "xml": XMLStringConverter,
        "xml_file": XMLFileConverter,
        "langchain": LangChainConverter,
    }
