from typing import Callable
from lionfuncs import save_to_file, read_file
from lion_core.protocols.adapter import Adapter
from lion_core.generic.note import Note
from lionagi.core.generic.registry.component.data_adapter import DataAdapter, JsonDataAdapter, XMLDataAdapter


class DataSourceAdapterConfig:
    
    data_adapter: DataAdapter = None
    data_adapter_config = {}
    
    save_func: Callable = save_to_file
    save_config: dict = {}

    read_func: Callable = read_file
    read_config: dict = {}
    
    def __init__(
        self,
        save_func: Callable = save_to_file,
        save_config: dict = {},
        read_func: Callable = read_file,
        read_config: dict = {},
        data_adapter_config: dict = {},
        data_adapter: DataAdapter = None
    ):
        self.data_adapter_config = data_adapter_config
        self.data_adapter = data_adapter
        if not self.data_adapter:
            self.data_adapter = DataAdapter(**self.data_adapter_config)
        self.save_func = save_func
        self.save_config = save_config
        self.read_func = read_func
        self.read_config = read_config
        
        
    def to_note(self):
        return Note(
            **{
                "save": {
                    "func": self.save_func,
                    "config": self.save_config
                },
                "read": {
                    "func": self.read_func,
                    "config": self.read_config
                },
                "data_adapter": self.data_adapter
            }
        )
        
         
class DataSourceAdapter(Adapter):
    
    config: Note
    
    @classmethod
    def from_obj(cls, subj_cls, obj, **kwargs) -> dict:
        """
        kwargs for read_func
        """
        kwargs = {**cls.config["read", "config"], **kwargs}
        obj = cls.config["read", "func"](obj, **kwargs)
        return cls.config["data_adapter"].from_obj(subj_cls, obj)
        
    
    @classmethod
    def to_obj(cls, subj, **kwargs) -> str:
        """
        kwargs for save_func
        """
        kwargs = {**cls.config["save", "config"], **kwargs}
        obj = cls.config["data_adapter"].to_obj(subj)
        return cls.config["save", "func"](obj, **kwargs)
        
    
json_file_config = DataSourceAdapterConfig(
    data_adapter = JsonDataAdapter,
    data_adapter_config = {},
    save_func = save_to_file,
    save_config = {},
    read_func = read_file,
    read_config = {},
)

xml_file_config = DataSourceAdapterConfig(
    data_adapter = XMLDataAdapter,
    data_adapter_config = {},
    save_func = save_to_file,
    save_config = {},
    read_func = read_file,
    read_config = {},
)


class JsonFileAdapater(DataSourceAdapter):
    
    obj_key = "json_file"    
    verbose = True
    config = json_file_config.to_note()
    
class XMLFileAdapter(DataSourceAdapter):
    
    obj_key = "xml_file"    
    verbose = True
    config = xml_file_config.to_note()