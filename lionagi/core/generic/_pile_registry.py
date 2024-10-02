from lion_core.generic.pile import Pile
from lion_core.pile_adapter import AdapterRegistry, Dumper, Loader



class XMLDumper(Dumper):
    default_directory: Path = Path(".") / "data" / "pile_dump" / "xml"
    default_filename: str = "unnamed_pile_dump_xml"
    obj_key = ".xml"

    @classmethod
    def dump_to(
        cls,
        subj: T,
        /,
        *,
        directory: Path | str = None,
        filename: str = None,
        timestamp: bool = True,
        root_tag: str = None,
        **kwargs,
    ):
        str_ = dict_to_xml(subj.to_dict(), root_tag=root_tag)
        save_to_file(
            str_,
            directory=directory or cls.default_directory,
            filename=filename or cls.default_directory,
            timestamp=timestamp,
            extension=cls.obj_key,
            **kwargs,
        )


class CSVDumper(Dumper):

    default_directory: Path = Path(".") / "data" / "pile_dump" / "csv"
    default_filename: str = "unnamed_pile_dump_csv"
    obj_key = ".csv"
    to_df = import_module("lionfuncs", "to_df")

    @classmethod
    def dump_to(
        cls,
        subj: T,
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
        df = cls.to_df(
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

        df.to_csv(filepath, **kwargs)


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