import json
from typing import Any

import pandas as pd

from lion_core.converter import (
    ConverterRegistry,
    DictConverter,
    JsonConverter,
    Converter,
)

from lionagi.os.libs import to_dict


class NodeConverterRegistry(ConverterRegistry): ...
