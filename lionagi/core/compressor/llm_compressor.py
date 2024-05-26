import asyncio
from lionagi import alcall
from lionagi.libs.ln_convert import to_list
import numpy as np
from lionagi.core.collections import iModel
from .base import TokenCompressor
from .util import tokenize, split_into_segments


# inspired by LLMLingua, MIT License, Copyright (c) Microsoft Corporation.
# https://github.com/microsoft/LLMLingua

class LLMCompressor(TokenCompressor):
    
    def __init__(self, imodel: iModel=None, system_msg=None, tokenizer=None, splitter=None):
        imodel = imodel or iModel(model="gpt-3.5-turbo")
        super().__init__(imodel=imodel, tokenizer=tokenizer, splitter=splitter)
        self.system_msg = system_msg or "You are tasked with compressing the following text for remembering in your memory"
        
    def tokenize(self, text):
        tokenize_func = self.tokenizer or tokenize
        return tokenize_func(text)
    
    def split(self, text):
        split_func = self.splitter or split_into_segments
        return split_func(text)
    
    async def calculate_perplexity_token_wise(self, context, **kwargs):
        tokens = self.tokenize(context)
        perplexity = await self._calculate_perpelxity_token_wise(tokens, **kwargs)
        return perplexity

    async def calculate_perplexity_segment_wise(self, text, initial_text=None, cumulative=False, **kwargs):
        segments = split_into_segments(text)
        _segments = []
        _context = initial_text or ""
        if cumulative:
            for i in range(1, len(segments)):
                _context += " " + segments[i-1]
                _segments.append(_context)
        else:
            _segments = segments
        
        segment_perplexities = await alcall(_segments, self.calculate_perplexity_token_wise, **kwargs)
        return {segment: perplexity for segment, perplexity in zip(segments, segment_perplexities)}

    async def compress(self, text, compression_ratio=0.15, initial_text=None, cumulative=False, **kwargs):
        
        kwargs["seed"] = kwargs.get("seed", 9630)
        segment_perplexity = await self.calculate_perplexity_segment_wise(text, cumulative, initial_text=initial_text, **kwargs)
        ranked_segments = self.rank_by_perplexity(segment_perplexity)
        return self.compress_segments(ranked_segments, compression_ratio)
        # compressed_segments =  
        # tokens = self.tokenize(compressed_segments)
        
        # prev_context = prev_context or ""
        # if cumulative:
        #     contexts = [prev_context+" ".join(tokens[:i]) for i in range(1, len(tokens))]
        # else:
        #     contexts = [prev_context+" "+i for i in tokens]
            
        # token_perplexity = await alcall(contexts, self.calculate_perplexity_token_wise, **kwargs)
        # token_perplexity = {tokens[i]: perplexity for i, perplexity in enumerate(token_perplexity)}
        # ranked_tokens = self.rank_by_perplexity(token_perplexity)
        # compressed_text = self.compress_tokens(ranked_tokens, compression_ratio)
        # return compressed_text
    
    @staticmethod
    def compress_tokens(tokens, compression_ratio=0.05):
        total_length = len(tokens)
        target_length = total_length * compression_ratio

        compressed_tokens = []
        current_length = 0

        for token in tokens:
            if current_length + len(token) <= target_length:
                compressed_tokens.append(token)
                current_length += len(token)
            else:
                # Optionally, truncate the token to fit the target length
                remaining_length = target_length - current_length
                compressed_tokens.append(token[:int(remaining_length)])
                break

        return " ".join(compressed_tokens)
    
    @staticmethod
    def rank_by_perplexity(_dict):
        items = list(_dict.keys())
        perplexities = list(_dict.values())
        item_perplexity_pairs = list(zip(items, perplexities))
        ranked_items = sorted(item_perplexity_pairs, key=lambda x: x[1], reverse=True)
        return ranked_items
    
    @staticmethod
    def compress_segments(ranked_segments, target_compression_ratio=0.5):
        total_length = sum(len(segment) for segment, _ in ranked_segments)
        target_length = total_length * target_compression_ratio

        compressed_segments = []
        current_length = 0

        for segment, _ in ranked_segments:
            if current_length + len(segment) <= target_length:
                compressed_segments.append(segment)
                current_length += len(segment)
            else:
                # Optionally, truncate the segment to fit the target length
                remaining_length = target_length - current_length
                compressed_segments.append(segment[:int(remaining_length)])
                break

        return " ".join(compressed_segments)
    
    async def _calculate_perpelxity_token_wise(self, tokens, **kwargs):
        _tasks = []        
        for i in range(len(tokens)):
            context = " ".join(tokens[:i])  # Join tokens to form the context
            messages = [
                {"role": "system", "content": self.system_msg},
                {"role": "user", "content": context},
            ]
            task = asyncio.create_task(self.imodel.call_chat_completion(messages=messages, logprobs=True, max_tokens=1, **kwargs))
            _tasks.append(task)
        
        results = await asyncio.gather(*_tasks)
        logprobs = [result[1]["choices"][0]["logprobs"]["content"] for result in results]
        logprobs = to_list(logprobs, flatten=True, dropna=True)
        logprobs = [lprob_["logprob"] for lprob_ in logprobs]
        return np.exp(np.mean(logprobs))
