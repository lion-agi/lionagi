from abc import ABC

from lionagi.core.collections import iModel


class TokenCompressor(ABC):
    """
    NOTICE:
        The token compressor system is inspired by LLMLingua.
        https://github.com/microsoft/LLMLingua

        MIT License
        Copyright (c) Microsoft Corporation.

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

    Authors:
        Huiqiang Jiang, Qianhui Wu, Chin-Yew Lin, Yuqing Yang, Lili Qiu
        @inproceedings{jiang-etal-2023-llmlingua,
            title = "{LLML}ingua: Compressing Prompts for Accelerated Inference of Large Language Models",
            author = "Huiqiang Jiang and Qianhui Wu and Chin-Yew Lin and Yuqing Yang and Lili Qiu",
            booktitle = "Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing",
            month = dec,
            year = "2023",
            publisher = "Association for Computational Linguistics",
            url = "https://aclanthology.org/2023.emnlp-main.825",
            doi = "10.18653/v1/2023.emnlp-main.825",
            pages = "13358--13376",
        }

    LionAGI Modifications:
        - Only borrowed the concept of token compression via perplexity
        - Removed the dependency on the LLMLingua library
        - use logprobs from GPT model to calculate perplexity
        - added async ability to the functions
        - used lionagi existing iModel class for API calls
    """

    def __init__(self, imodel: iModel, tokenizer=None, splitter=None):
        self.imodel = imodel
        self.tokenizer = tokenizer
        self.splitter = splitter
