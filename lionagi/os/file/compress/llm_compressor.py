# from .base import TokenCompressor


# from lion_core.libs import to_list


# from lionagi.os.sys_util import SysUtil
# from lionagi.os.operator.imodel.imodel import iModel

# from lionagi.os.file.tokenize.utils import tokenize
# from lionagi.os.file.chunk.utils import chunk_by_chars, chunk_by_tokens


# class LLMCompressor(TokenCompressor):

#     def __init__(
#         self,
#         imodel: iModel = None,
#         system_msg=None,
#         tokenizer=None,  # must be a callable or object with a tokenize method
#         splitter=None,  # must be a callable or object with a split/chunk/segment method
#         target_ratio=0.2,
#         n_samples=5,  # the cumulative samples to take in each perplexity calculation
#         chunk_size=64,
#         max_tokens_per_sample=80,
#         min_compression_score=0,  # (0-1) the minimum score to consider for compression, 0 means all
#         split_overlap=0,
#         split_threshold=0,
#         verbose=True,
#     ):
#         imodel = imodel or iModel(model="gpt-3.5-turbo", temperature=0.3)
#         super().__init__(imodel=imodel, tokenizer=tokenizer, splitter=splitter)
#         self.system_msg = (
#             system_msg
#             or "Concisely summarize and compress the information for storage:"
#         )
#         self.target_ratio = target_ratio
#         self.n_samples = n_samples
#         self.chunk_size = chunk_size
#         self.max_tokens_per_sample = max_tokens_per_sample
#         self.min_compression_score = min_compression_score
#         self.verbose = verbose
#         self.split_overlap = split_overlap
#         self.split_threshold = split_threshold

#     def tokenize(self, text, encoding_name=None, return_byte=False, **kwargs):
#         """
#         by default you can use `encoding_name` to be one of,
#         ['gpt2', 'r50k_base', 'p50k_base', 'p50k_edit', 'cl100k_base', 'o200k_base']

#         or you can use `encoding_model` that tiktoken supports in their mapping such as "gpt-4o"
#         """
#         if not self.tokenizer:
#             return tokenize(
#                 text,
#                 encoding_model=self.imodel.iModel_name,
#                 encoding_name=encoding_name,
#                 return_byte=return_byte,
#             )

#         if hasattr(self.tokenizer, "tokenize"):
#             return self.tokenizer.tokenize(text, **kwargs)

#         return self.tokenizer(text, **kwargs)

#     def split(
#         self,
#         text,
#         chunk_size=None,
#         overlap=None,
#         threshold=None,
#         by_chars=False,
#         return_tokens=False,
#         return_byte=False,
#         **kwargs,
#     ):
#         if not self.splitter:
#             splitter = chunk_by_chars if by_chars else chunk_by_tokens
#             return splitter(
#                 text,
#                 chunk_size or self.chunk_size,
#                 overlap or self.split_overlap,
#                 threshold or self.split_threshold,
#                 return_tokens=return_tokens,
#                 return_byte=return_byte,
#             )

#         a = [
#             getattr(self.splitter, i, None)
#             for i in ["split", "chunk", "segment"]
#             if i is not None
#         ][0]
#         a = getattr(self.splitter, a)
#         return a(text, **kwargs)

#     async def compress(
#         self,
#         text,
#         target_ratio=None,
#         initial_text=None,
#         cumulative=False,
#         split_kwargs=None,
#         split_overlap=None,
#         split_threshold=None,
#         rank_by="perplexity",
#         min_compression_score=None,
#         verbose=True,
#         **kwargs,
#     ):
#         start = SysUtil.time()
#         if split_kwargs is None:
#             split_kwargs = {}
#             split_kwargs["chunk_size"] = self.max_tokens_per_sample
#             split_kwargs["overlap"] = split_overlap or 0
#             split_kwargs["threshold"] = split_threshold or 0

#         len_tokens = len(self.tokenize(text))

#         items = self.split(text, return_tokens=True, **split_kwargs)

#         if rank_by == "perplexity":
#             ranked_items = await self.rank_by_pplex(
#                 items=items, initial_text=initial_text, cumulative=cumulative, **kwargs
#             )

#             prompt_tokens = sum([i[1]["num_prompt_tokens"] for i in ranked_items])

#             num_completion_tokens = sum(
#                 [i[1]["num_completion_tokens"] for i in ranked_items]
#             )

#             price = (
#                 prompt_tokens * 0.5 / 1000000 + num_completion_tokens * 1.5 / 1000000
#             )

#             selected_items = self.select_by_pplex(
#                 ranked_items=ranked_items,
#                 target_compression_ratio=target_ratio or self.target_ratio,
#                 original_length=len_tokens,
#                 min_pplex=min_compression_score or self.min_compression_score,
#             )

#             if verbose:
#                 msg = ""
#                 msg += f"Original Token number: {len_tokens}\n"

#                 def _f(i):
#                     if isinstance(i, str):
#                         i = self.tokenize(i)

#                     if isinstance(i, list):
#                         return len(to_list(i, dropna=True, flatten=True))

#                 len_ = sum([_f(i) for i in selected_items])
#                 msg += f"Selected Token number: {len_}\n"
#                 msg += f"Token Compression Ratio: {len_ / len_tokens:.03f}\n"
#                 msg += f"Compression Time: {SysUtil.time() - start:.04f} seconds\n"
#                 msg += f"Compression Model: {self.imodel.iModel_name}\n"
#                 msg += f"Compression Method: {rank_by}\n"
#                 msg += f"Compression Usage: ${price:.05f}\n"
#                 print(msg)

#             a = "".join([i.strip() for i in selected_items]).strip()
#             a = a.replace("\n\n", "")
#             return a

#         raise ValueError(f"Ranking method {rank_by} is not supported")
