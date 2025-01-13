from typing import TYPE_CHECKING, Literal

from lionagi.service.imodel import iModel

if TYPE_CHECKING:
    from lionagi.session.branch import Branch


async def translate(
    branch: "Branch",
    text: str,
    technique: Literal["SynthLang"] = "SynthLang",
    technique_kwargs: dict = None,
    compress: bool = False,
    chat_model: iModel = None,
    compress_model: iModel = None,
    compression_ratio: float = 0.2,
    compress_kwargs=None,
    verbose: bool = True,
    new_branch: bool = True,
    **kwargs,
):
    if technique == "SynthLang":
        from lionagi.libs.token_transform.synthlang import (
            translate_to_synthlang,
        )

        if not technique_kwargs:
            technique_kwargs = {}
        if not technique_kwargs.get("template_name"):
            technique_kwargs["template_name"] = "symbolic_systems"

        technique_kwargs = {**technique_kwargs, **kwargs}

        return await translate_to_synthlang(
            text=text,
            compress=compress,
            chat_model=chat_model or branch.chat_model,
            compress_model=compress_model,
            compression_ratio=compression_ratio,
            compress_kwargs=compress_kwargs,
            verbose=verbose,
            branch=branch if not new_branch else None,
            **technique_kwargs,
        )

    raise ValueError(f"Technique {technique} is not supported.")
