from collections.abc import Callable
from pathlib import Path
from typing import Literal

from lionagi.service.imodel import iModel
from lionagi.session.branch import Branch
from lionagi.utils import alcall, get_bins

from .base import TokenMapping, TokenMappingTemplate
from .synthlang_.base import SynthlangFramework, SynthlangTemplate

FRAMEWORK_OPTIONS = SynthlangFramework.load_framework_options()
FRAMEWORK_CHOICES = Literal["math", "optim", "custom_algebra"]
DEFAULT_INVOKATION_PROMPT = (
    "The light-speed brown fox jumps over the lazy dog with great agility."
)


async def symbolic_compress_context(
    *,
    text: str = None,
    url_or_path: str | Path = None,
    chunk_by="tokens",
    chunk_size: int = 1000,
    chunk_tokenizer: Callable = None,
    threshold=50,
    output_path: Path | str = None,
    overlap=0.025,
    system: str = None,
    chat_model: iModel = None,
    use_lion_system_message: bool = True,
    max_concurrent=10,
    throttle_period=1,
    framework: Literal["synthlang"] = "synthlang",
    framework_template: (
        SynthlangTemplate | SynthlangFramework
    ) = SynthlangTemplate.REFLECTIVE_PATTERNS,
    framework_options: list[FRAMEWORK_CHOICES] = None,
    compress: bool = False,
    compress_model: iModel = None,
    compression_ratio: float = 0.2,
    compress_initial_text=None,
    compress_cumulative=False,
    compress_split_kwargs=None,
    compress_min_pplx=None,
    encode_token_map: TokenMappingTemplate | dict | TokenMapping = None,
    num_encodings: int = 3,
    encode_output: bool = True,
    num_output_encodings: int = 1,
    verbose: bool = True,
    branch: Branch = None,
    additional_text: str = "",
    **kwargs,
):
    if framework != "synthlang":
        raise ValueError(f"Unsupported framework: {framework}")

    if not text and not url_or_path:
        raise ValueError("Either text or url_or_path must be provided.")

    if text and url_or_path:
        raise ValueError("Only one of text or url_or_path should be provided.")

    from .synthlang_.translate_to_synthlang import translate_to_synthlang

    async def _inner(text: str):
        b_ = None
        if branch:
            b_ = await branch.aclone()
        else:
            b_ = Branch(
                system=system,
                use_lion_system_message=use_lion_system_message,
                chat_model=chat_model,
            )

        return await translate_to_synthlang(
            text,
            branch=b_,
            framework_template=framework_template,
            framework_options=framework_options,
            compress=compress,
            compress_model=compress_model,
            compression_ratio=compression_ratio,
            compress_kwargs={
                "initial_text": compress_initial_text,
                "cumulative": compress_cumulative,
                "split_kwargs": compress_split_kwargs,
                "min_pplx": compress_min_pplx,
            },
            encode_token_map=encode_token_map,
            num_encodings=num_encodings,
            encode_output=encode_output,
            num_output_encodings=num_output_encodings,
            verbose=verbose,
            additional_text=additional_text,
            **kwargs,
        )

    from lionagi.libs.file.process import chunk, chunk_content

    chunks = []
    if url_or_path:
        chunks = chunk(
            url_or_path=url_or_path,
            chunk_by=chunk_by,
            chunk_size=chunk_size,
            overlap=overlap,
            threshold=threshold,
        )

    elif text:
        chunks = chunk_content(
            text=text,
            chunk_by=chunk_by,
            chunk_size=chunk_size,
            overlap=overlap,
            threshold=threshold,
            tokenizer=chunk_tokenizer or str.split,
        )

    texts = [str(i).strip() for i in chunks if str(i).strip()]
    bins = get_bins(texts, upper=chunk_size)
    textss = []
    for i in bins:
        textss.append("\n".join([texts[j] for j in i]))

    results = await alcall(
        textss,
        _inner,
        max_concurrent=max_concurrent,
        retry_default=None,
        num_retries=3,
        throttle_period=throttle_period,
        retry_delay=1,
        backoff_factor=2,
        flatten=True,
        dropna=True,
        unique_output=True,
    )
    text = "\n".join(results)
    text = DEFAULT_INVOKATION_PROMPT + text

    if output_path:
        fp = Path(output_path)
        fp.write_text(text)
        if verbose:
            print(f"Results of {len(text)} characters saved to: {fp}")

        return fp
    return text
