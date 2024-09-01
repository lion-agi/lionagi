from typing import Any, TypeVar
from lionagi.os.sys_utils import SysUtil

T = TypeVar("T")


def to_langchain_document(**kwargs: Any) -> Any:

    Document = SysUtil.check_import(
        package_name="langchain",
        module_name="schema",
        import_name="Document",
    )

    kwargs["page_content"] = kwargs.pop("content", None)
    kwargs["lc_id"] = kwargs.pop("ln_id", None)
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    if "page_content" not in kwargs:
        kwargs["page_content"] = ""

    return Document(**kwargs)
