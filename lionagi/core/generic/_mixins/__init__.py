from ._field import ComponentFieldMixin
from ._metadata import ComponentMetaManageMixin
from ._validation import ComponentValidationMixin
from ._pandas import PandasComponentMixin
from ._pydantic import PydanticComponentMixin
from ._langchain import LangChainComponentMixin
from ._llama_index import LlamaIndexComponentMixin


class ComponentMixin(
    ComponentFieldMixin,
    ComponentMetaManageMixin,
    ComponentValidationMixin,
    PandasComponentMixin,
    PydanticComponentMixin,
    LangChainComponentMixin,
    LlamaIndexComponentMixin,
):
    pass
