# from lionagi.core.collections import iModel
# from .base import TokenCompressor


# class LLMSummarizer(TokenCompressor):

#     def __init__(
#         self, imodel: iModel = None, system_msg=None, tokenizer=None, splitter=None,
#         max_tokens=25, target_ratio=0.3
#     ):
#         imodel = imodel or iModel(model="gpt-3.5-turbo", max_tokens=max_tokens)
#         super().__init__(imodel=imodel, tokenizer=tokenizer, splitter=splitter)
#         self.system_msg = (
#             system_msg
#             or "Summarize the following sentence to be concise and informative:"
#         )
#         self.target_ratio = target_ratio

#     async def summarize_sentence(self, sentence, **kwargs):
#         messages = [
#             {"role": "system", "content": self.system_msg},
#             {"role": "user", "content": sentence},
#         ]
#         response = await self.imodel.call_chat_completion(messages, **kwargs)
#         return response["choices"][0]["message"]["content"]

#     def tokenize(self, text):
#         tokenize_func = self.tokenizer or tokenize
#         return tokenize_func(text)

#     def split(self, text):
#         split_func = self.splitter or split_into_segments
#         return split_func(text)

#     # Function to enforce maximum sentence length
#     def enforce_max_sentence_length(self, sentence, max_words=25):
#         words = self.tokenize(sentence)
#         if len(words) > max_words:
#             sentence = ' '.join(words[:max_words])
#         return sentence

#     async def summarize_text(self, text, max_length_per_sentence=25, target_ratio=None, **kwargs):
#         sentences = self.split(text)
#         summarized = await alcall(
#             sentences, self.summarize_sentence, **kwargs
#         )
#         summarized = [
#             self.enforce_max_sentence_length(sentence, max_length_per_sentence)
#             for sentence in summarized
#         ]

#         original_length = len(self.tokenize(text))
#         summarized_length = len(self.tokenize(' '.join(summarized)))
#         current_ratio = summarized_length / original_length

#         target_ratio = target_ratio or self.target_ratio
#         if current_ratio > target_ratio:
#             words_to_remove = int((current_ratio - target_ratio) * original_length)
#             return ' '.join(summarized[:-words_to_remove])

#         return ' '.join(summarized)
