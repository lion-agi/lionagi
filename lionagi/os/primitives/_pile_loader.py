from pathlib import Path
from typing import Any
import pandas as pd
from lion_core.pile_loader import PileLoaderRegistry as PLR, PileLoader
from lionagi.os import lionfuncs as ln


class PileLoaderRegistry(PLR):
    pass


class CSVLoader(PileLoader):

    @staticmethod
    def from_obj(cls, obj: str | Path, **kwargs) -> list[dict]:
        if isinstance(obj, str):
            obj = Path(obj)
        return pd.read_csv(obj).to_dict(orient="records")

    @staticmethod
    def can_load(cls, obj: Path | str, **kwargs) -> bool:
        if isinstance(obj, str):
            obj = Path(obj)
        return obj.suffix == ".csv"


class PandasDataFrameLoader(PileLoader):

    @staticmethod
    def from_obj(cls, obj: pd.DataFrame, **kwargs) -> list[dict]:
        return obj.to_dict(orient="records")

    @staticmethod
    def can_load(cls, obj: Any, **kwargs) -> bool:
        return isinstance(obj, pd.DataFrame)


class LlamaIndexVectorStoreLoader(PileLoader):

    @staticmethod
    def from_obj(cls, obj: str | Path, **kwargs) -> list[dict] | list[list[dict]]:
        from lionagi.app.LlamaIndex.loader import load_llamaindex_vector_store

        return load_llamaindex_vector_store(obj)

    @staticmethod
    def can_load(cls, obj: Path | str, **kwargs) -> bool:
        if isinstance(obj, str):
            obj = Path(obj)

        files = list(obj.iterdir())
        check_files = ["default__vector_store", "docstore", "index_store"]
        check_files = [f"{obj}/{file}.json" for file in check_files]

        if all(file in files for file in check_files):
            return True
        return False


class LlamaIndexFileLoader(PileLoader):

    @staticmethod
    def from_obj(cls, obj: Path | str, **kwargs) -> list[dict]:
        from lionagi.app.LlamaIndex.bridge import LlamaIndexBridge

        kwargs["reader_args"] = kwargs.get("reader_args", [])
        kwargs["reader_args"] = (
            kwargs["reader_args"]
            if isinstance(kwargs["reader_args"], list)
            else [kwargs["reader_args"]]
        )
        kwargs["reader_args"].insert(0, obj)
        docs = LlamaIndexBridge.load_file(**kwargs)
        return [ln.to_dict(doc) for doc in docs]

    @staticmethod
    def can_load(cls, obj: Path | str, **kwargs) -> bool:
        if isinstance(obj, str):
            obj = Path(obj)
        if obj.is_dir():
            if "reader_kwargs" in kwargs and kwargs["reader_kwargs"].get(
                "recursive", False
            ):
                return True
        elif obj.is_file():
            return True
        return False


PileLoaderRegistry.register("pandas_dataframe", PandasDataFrameLoader)
PileLoaderRegistry.register("llama_index_vector_store", LlamaIndexVectorStoreLoader)
PileLoaderRegistry.register("llama_index_read_file", LlamaIndexFileLoader)


__all__ = ["PileLoaderRegistry", "PileLoader"]
