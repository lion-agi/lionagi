import asyncio
from lionagi import alcall
from lionagi.libs.ln_convert import to_list
import numpy as np
from lionagi.core.collections import iModel
from .base import TokenCompressor
from .util import tokenize, split_into_segments


class LLMSummarizer(TokenCompressor):

    def __init__(self, imodel: iModel, tokenizer=None, system_msg=None, splitter=None):
        super().__init__(imodel, tokenizer, splitter)
