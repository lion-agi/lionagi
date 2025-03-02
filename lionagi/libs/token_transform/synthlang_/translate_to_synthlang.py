from timeit import default_timer as timer
from typing import Literal

from lionagi.service.imodel import iModel
from lionagi.session.branch import Branch

from ..base import TokenMapping, TokenMappingTemplate
from .base import SynthlangFramework, SynthlangTemplate

FRAMEWORK_OPTIONS = SynthlangFramework.load_framework_options()
FRAMEWORK_CHOICES = Literal["math", "optim", "custom_algebra"]


async def translate_to_synthlang(
    text: str,
    /,
    chat_model: iModel = None,
    framework_template: (
        SynthlangTemplate | SynthlangFramework
    ) = SynthlangTemplate.REFLECTIVE_PATTERNS,
    framework_options: list[FRAMEWORK_CHOICES] = None,
    compress: bool = False,
    compress_model: iModel = None,
    compression_ratio: float = 0.2,
    compress_kwargs=None,
    encode_token_map: TokenMappingTemplate | dict | TokenMapping = None,
    num_encodings: int = 3,
    encode_output: bool = False,
    num_output_encodings: int = None,
    verbose: bool = True,
    branch: Branch = None,
    additional_text: str = "",
    **kwargs,
):
    start = timer()
    if encode_output and num_output_encodings is None:
        num_output_encodings = 1

    if encode_token_map is not None:
        if not isinstance(num_encodings, int) or num_encodings < 1:
            raise ValueError(
                "num_encodings must be at least 1 if encode_token_map is provided"
            )
        if isinstance(encode_token_map, TokenMappingTemplate | str):
            encode_token_map = TokenMapping.load_from_template(
                encode_token_map
            )
            additional_text += (
                f"\nTransforming text with {encode_token_map.metadata['title']}"
                f"\nOverview: {encode_token_map.metadata['overview']}"
            )
            encode_token_map = encode_token_map.content
        if not isinstance(encode_token_map, dict):
            raise ValueError(
                "encode_token_map must be a dict or TokenMappingTemplate"
            )
        for _ in range(num_encodings):
            text = " ".join(
                [str(i).strip() for i in text.split() if i.strip()]
            )
            for k, v in encode_token_map.items():
                text = text.replace(k, v)
                text = text.strip()
        additional_text += (
            f"\nthesaurus, lexicon, glossary:\n{encode_token_map}"
        )
    if not isinstance(framework_template, SynthlangFramework):
        framework_template = SynthlangFramework.load_from_template(
            framework_template
        )

    final_prompt = framework_template.create_system_prompt(
        framework_options, additional_text
    )

    if compress:
        from ..perplexity import compress_text

        text = await compress_text(
            text,
            chat_model=compress_model or chat_model,
            compression_ratio=compression_ratio,
            verbose=verbose,
            **(compress_kwargs or {}),
        )

    sys1 = None
    sys2 = final_prompt
    if branch and branch.system:
        sys1 = branch.system
        branch.msgs.add_message(system=sys2)

    else:
        branch = Branch(system=final_prompt, chat_model=chat_model)

    from lionagi.service.endpoints.token_calculator import TokenCalculator

    calculator = TokenCalculator()

    len_tokens = calculator.tokenize(text, return_tokens=False)

    kwargs["guidance"] = (
        "Following SynthLang, translate the provided text into SynthLang syntax. "
        "Reasonably reduce the token count by up to 80%. Return only the transformed"
        " string enclosed by ```synthlang...```. \n\n"
        "DO NOT include anything else, no comments, no explanations, no additional "
        "text, just the transformed string." + kwargs.get("guidance", "")
    )

    out = await branch.chat(
        instruction=f"Converts the given text into SynthLang's hyper-efficient format.",
        context="Text to convert:\n\n" + text,
        chat_model=chat_model or branch.chat_model,
        **kwargs,
    )
    out = str(out).strip()

    if encode_output:
        if isinstance(num_output_encodings, int) and num_output_encodings > 0:
            for _ in range(num_output_encodings):
                out = " ".join(
                    [str(i).strip() for i in out.split(" ") if i.strip()]
                )
                for k, v in encode_token_map.items():
                    out = out.replace(k, v).strip()

    if sys1:
        branch.msgs.add_message(system=sys1)

    len_ = calculator.tokenize(out)
    if verbose:
        msg = "------------------------------------------\n"
        msg += f"Compression Method: SynthLang\n"
        msg += f"Compressed Token number: {len_}\n"
        msg += f"Token Compression Ratio: {len_ / len_tokens:.1%}\n"
        msg += f"Compression Time: {timer() - start:.03f} seconds\n"
        msg += f"Compression Model: {branch.chat_model.model_name}\n"
        print(msg)

    return out
