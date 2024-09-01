# import asyncio
# from lionagi import alcall
# from lionagi.libs.ln_convert import to_list
# import numpy as np

# def split_into_segments(text):
#     segments = text.split(".")  # Splitting by period followed by a space
#     return [segment.strip() for segment in segments if segment]

# # Tokenize the segment
# def tokenize(segment):
#     tokens = segment.split()  # Simple space-based tokenization
#     return tokens

# async def calculate_perplexity(system_msg: str, imodel, tokens, initial_context=None, **kwargs):
#     _tasks = []
#     _context = initial_context or ""
#     for i in range(len(tokens)):
#         _context += " " + tokens[i]
#         messages = [
#             {"role": "system", "content": system_msg},
#             {"role": "user", "content": _context},
#         ]
#         task = asyncio.create_task(
#             imodel.call_chat_completion(
#                 messages=messages, logprobs=True, max_tokens=1, **kwargs
#             )
#         )
#         _tasks.append(task)

#     results = await asyncio.gather(*_tasks)
#     logprobs = [
#         result[1]["choices"][0]["logprobs"]["content"] for result in results
#     ]
#     logprobs = to_list(logprobs, flatten=True, dropna=True)
#     logprobs = [lprob_["logprob"] for lprob_ in logprobs]
#     return np.exp(np.mean(logprobs))

# async def rank_by_perplexity(
#     text: str | list[str] = None,   # if list we assume they are already well split
#     initial_text=None,

#     segments,
#     initial_text=None,
#     cumulative=False,
#     **kwargs
# ):
#     _segments = []
#     _context = initial_text or ""
#     _task = []

#     if cumulative:
#         for i in range(1, len(segments)):
#             _context += " " + segments[i - 1]
#             _segments.append(_context)
#     else:
#         _segments = segments

#     for i in segments:
#         _task.append(asyncio.create_task(
#             calculate_perplexity(
#                 self.system_msg, self.imodel, self.tokenize(i), **kwargs)
#             )
#         )
#     segment_perplexities = await asyncio.gather(*_task)

#     return {
#         segment: perplexity
#         for segment, perplexity in zip(segments, segment_perplexities)
#     }
