from .base_node import BaseNode
from .data_logger import DataLogger


class MessageNode(BaseNode):
    role: str
    name: str
    _logger: 'DataLogger' = DataLogger()

    # def from_oai(self):
    #     ...