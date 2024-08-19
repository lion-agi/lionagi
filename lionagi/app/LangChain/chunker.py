from typing import Callable


def langchain_text_splitter(
    data: str | list[str],
    splitter: str | Callable,
    /,
    *splitter_args,
    **splitter_kwargs,
) -> list[str]:
    from lionagi.os.sys_util import SysUtil

    text_splitter = SysUtil.check_import(
        package_name="langchain_text_splitters",
        pip_name="langchain",
    )

    try:
        if isinstance(splitter, str):
            splitter = getattr(text_splitter, splitter)
        else:
            splitter = splitter
    except Exception as e:
        raise ValueError(f"Invalid text splitter: {splitter}. Error: {e}")

    try:
        splitter_obj = splitter(*splitter_args, **splitter_kwargs)
        if isinstance(data, str):
            chunk = splitter_obj.split_text(data)
        else:
            chunk = splitter_obj.split_documents(data)
        return chunk
    except Exception as e:
        raise ValueError(f"Failed to split. Error: {e}")
