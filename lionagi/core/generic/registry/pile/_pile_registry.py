from typing import Any, TypeVar
from pathlib import Path
import json
from lion_core.generic.pile import Pile
from lion_core.pile_adapter import AdapterRegistry, Dumper, Loader
import pandas as pd
from lionfuncs import to_dict, dict_to_xml, save_to_file, create_path, to_df, read_file


DEFAULT_SAVE_DIRECTORY: Path = Path(".") / "data" / "pile_dump"
DEFAULT_FILENAME: str = "unnamed_pile_dump"




class JsonFileDumper(Dumper):

    default_directory: Path = DEFAULT_SAVE_DIRECTORY / "json"
    default_filename: str = DEFAULT_FILENAME + "_json"
    obj_key = "json"

    @classmethod
    def dump_to(
        cls,
        subj: Pile,
        /,
        **kwargs,
    ) -> Path:
        """
        kwargs for save to file
        """
        str_ = json.dumps(subj.to_dict())
        fp = save_to_file(
            str_,
            extension=cls.obj_key,
            **kwargs,
        )
        return fp

        
class JsonDataLoader(Loader):

    obj_key = "json"

    @classmethod
    def load_from(
        cls,
        obj: str,
        recursive: bool = False,
        recursive_python_only: bool = True,
        **kwargs: Any,
    ) -> dict:
        return to_dict(
            obj,
            recursive=recursive,
            recursive_python_only=recursive_python_only,
            **kwargs,
        )


class JsonFileLoader(Loader):

    obj_key = ".json"

    @classmethod
    def load_from(
        cls,
        obj: str,
        recursive: bool = False,
        recursive_python_only: bool = True,
        **kwargs: Any,
    ) -> dict:
        dict_ = json.load(obj)
        return to_dict(
            dict_,
            recursive=recursive,
            recursive_python_only=recursive_python_only,
            **kwargs,
        )


class XMLFileDumper(Dumper):
    default_directory: Path = DEFAULT_SAVE_DIRECTORY / "xml"
    default_filename: str = DEFAULT_FILENAME + "_xml"
    obj_key = ".xml"

    @classmethod
    def dump_to(
        cls,
        subj: Pile,
        /,
        *,
        directory: Path | str = None,
        filename: str = None,
        timestamp: bool = True,
        root_tag: str = None,
        **kwargs,
    ) -> Path:
        str_ = dict_to_xml(subj.to_dict(), root_tag=root_tag)
        fp = save_to_file(
            str_,
            directory=directory or cls.default_directory,
            filename=filename or cls.default_directory,
            timestamp=timestamp,
            extension=cls.obj_key,
            **kwargs,
        )
        return fp


class XMLDataLoader(Loader):
    obj_key = "xml"

    @classmethod
    def load_from(
        cls,
        obj,
        /,
        **kwargs
    ) -> dict:
        kwargs['str_type'] = "xml"
        return to_dict(obj, **kwargs)



class XMLFileLoader(Loader):
    obj_key = ".xml"

    @classmethod
    def load_from(
        cls,
        obj,
        /,
        **kwargs
    ) -> dict:
        str_ = read_file(obj)
        kwargs['str_type'] = "xml"
        return to_dict(str_, **kwargs)




class CSVFileLoader(Loader):
    obj_key = ".csv"
    
    @classmethod
    def load_from(
        cls,
        obj: str,
        /,
        **kwargs: Any,
    ) -> list[dict]:
        df = pd.read_csv(obj)
        dicts = df.to_dict(orient="records", index=False)
        return [to_dict(i, **kwargs) for i in dicts]


class CSVDumper(Dumper):

    default_directory: Path = DEFAULT_SAVE_DIRECTORY / "csv"
    default_filename: str = DEFAULT_FILENAME + "_csv"
    obj_key = ".csv"

    @classmethod
    def dump_to(
        cls,
        subj: Pile,
        /,
        *,
        directory: Path | str = None,
        filename: str = None,
        timestamp: bool = True,
        drop_how: str = "all",
        drop_kwargs: dict | None = None,
        reset_index: bool = True,
        concat_kwargs: dict | None = None,
        pd_kwargs: dict = None,
        **kwargs,
    ):
        dicts_ = [i.to_dict() for i in subj]

        df = to_df(
            dicts_,
            drop_how=drop_how,
            drop_kwargs=drop_kwargs,
            reset_index=reset_index,
            concat_kwargs=concat_kwargs,
            **(pd_kwargs or {}),
        )
        
        filepath = create_path(
            directory=directory or cls.default_directory,
            filename=filename or cls.default_filename,
            timestamp=timestamp,
            extension=cls.obj_key,
            **kwargs,
        )
        
        df.to_csv(filepath, index=False)
        return filepath



    # load / dump methods, should be added in lionagi

    @classmethod
    def _get_adapter_registry(cls) -> AdapterRegistry:
        if isinstance(cls._adapter_registry, type):
            cls._adapter_registry = cls._adapter_registry()
        return cls._adapter_registry
    
    @classmethod
    def load(cls, obj: Any, obj_key: str = None, /, **kwargs: Any) -> Pile:
        try:
            item = cls._get_adapter_registry().load(obj, obj_key, **kwargs)
            if isinstance(item, list):
                return cls([Component.from_obj(i) for i in item])
            if isinstance(item, dict):
                if "pile" in item:
                    return cls.from_dict(item)
                return cls([Component.from_obj(i) for i in item])
            return cls([Component.from_obj(item)])
        except Exception as e:
            raise LionTypeError(f"Failed to load pile. Error: {e}")

    def dump(self, obj_key, *, clear=False, **kwargs) -> None:
        try:
            self._get_adapter_registry().dump(self, obj_key, **kwargs)
            if clear:
                self.clear()
        except Exception as e:
            raise LionTypeError(f"Failed to dump pile. Error: {e}")

    @async_synchronized
    async def adump(self, *args, **kwargs) -> dict:
        self.dump(*args, **kwargs)


    @classmethod
    def load(cls, data: dict, **kwargs: Any) -> Pile:
        return cls.from_dict(data)

    def to_df(self):
        """Return the pile as a DataFrame."""
        dicts_ = []
        for i in self.values():
            _dict = i.to_dict()
            if _dict.get("embedding", None):
                _dict["embedding"] = str(_dict.get("embedding"))
            dicts_.append(_dict)
        return to_df(dicts_)


class PileAdapterRegistry(AdapterRegistry):
    ...
    
    
__all__ = ["PileAdapterRegistry"]