from ..utils.call_utils import l_call
from ..schema import BaseNode, DataLogger


class MessageNode(BaseNode):
    role: str
    name: str
    _logger: 'DataLogger' = DataLogger()

    # def from_oai(self):
    #     ...
    
    def to_csv(self):
        pass

    # def to_csv(self, filename=None,dir=None,  verbose=True, timestamp=True, dir_exist_ok=True, file_exist_ok=False):
    #     self._logger.to_csv(filename,dir=dir, verbose=verbose, timestamp=timestamp, dir_exist_ok=dir_exist_ok, file_exist_ok=file_exist_ok)
