import logging
from typing import Callable
from lionagi.os.sys_util import SysUtil
from lionagi.os.file.tokenize.token_calculator import TextTokenCalculator
from lionagi.app.TikToken.config import DEFAULT_CONFIG


class TikTokenCalculator(TextTokenCalculator):

    tiktoken = SysUtil.check_import("tiktoken")
    config = DEFAULT_CONFIG

    @classmethod
    def calculate(
        cls,
        s_: str = None,
        /,
        encoding_name: str | None = None,
        model_name: str | None = None,
        tokenizer: Callable | None = None,
    ) -> int:

        return cls._calculate(
            s_,
            encoding_name=encoding_name,
            model_name=model_name,
            tokenizer=tokenizer,
        )

    @classmethod
    def _calculate(
        cls,
        s_: str = None,
        /,
        encoding_name: str | None = None,
        model_name: str | None = None,
        tokenizer: Callable | None = None,
    ) -> int:

        if not s_:
            return 0

        model_name = model_name or cls.config["model_name"]
        tokenizer = tokenizer or cls.config["tokenizer"]

        if not callable(tokenizer):
            if model_name:
                try:
                    encoding_name = encoding_name or cls.tiktoken.encoding_for_model(
                        model_name
                    )
                except:
                    encoding_name = encoding_name or cls.config["encoding_name"]
            tokenizer = cls.tiktoken.get_encoding(encoding_name).encode
        try:
            return len(a := tokenizer(s_)) if not isinstance(a, int) else a
        except Exception as e:
            logging.error(f"Error in tokenizing text with custom tokenizer, {e}")
