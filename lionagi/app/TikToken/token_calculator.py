from lionagi.os.sys_utils import SysUtil
from lionagi.os.file.tokenize.token_calculator import TextTokenCalculator

from .config import DEFAULT_CONFIG


class TikTokenCalculator(TextTokenCalculator):

    tiktoken = SysUtil.import_module("tiktoken")
    config = DEFAULT_CONFIG

    def _calculate(self, s_, **kwargs):
        if kwargs:
            self.update_config(**kwargs)
        return self.tokenize(s_)

    def tokenize(
        self,
        s_=None,
        /,
        return_tokens: bool = False,
        return_byte: bool = False,
    ):
        if not s_:
            return 0

        tokenizer = self.tokenizer
        encoding = None

        if not callable(tokenizer):
            if self.model_name:
                try:
                    encoding_name = self.tiktoken.encoding_for_model(self.model_name)
                except:
                    encoding_name = self.encoding_name
            else:
                encoding_name = self.encoding_name
            encoding = self.tiktoken.get_encoding(encoding_name)

            special_encodings = (
                [encoding.encode(token) for token in self.disallowed_tokens]
                if self.disallowed_tokens
                else []
            )
            codes = encoding.encode(s_)

            if special_encodings and len(special_encodings) > 0:
                codes = [code for code in codes if code not in special_encodings]

            if return_byte:
                return codes

            if return_tokens:
                return [encoding.decode([code]) for code in codes]
            return len(codes)

        tokens = tokenizer(s_)
        valid_tokens = [
            token for token in tokens if token not in self.disallowed_tokens
        ]
        return valid_tokens if return_tokens else len(valid_tokens)
