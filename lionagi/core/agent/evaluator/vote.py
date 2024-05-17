# TODO

# from lionagi.libs import func_call
# import numpy as np
# from lionagi.core.form.predict import predict
# from lionagi.core.form.score import score


# async def vote(
#     sentence,
#     directive=predict,
#     num_generations=5,
#     num_output=1,
#     num_scorer=5,
#     score_range=(0, 100),
#     num_digit=2,
#     scorer_instruction=None,
#     **kwargs,
# ):
#     async def _inner(i):
#         out_ = await directive(sentence, **kwargs)
#         score_ = await score(
#             out_.answer,
#             context=sentence,
#             instruction=scorer_instruction,
#             score_range=score_range,
#             num_digit=num_digit,
#             num_instances=num_scorer,
#             return_template=False,
#         )

#         out_.__setattr__("score", score_)
#         return out_

#     _outs = await func_call.alcall(list(range(num_generations)), _inner)

#     top_index = np.argsort([i.score for i in _outs])[-num_output:]
#     final_output = list(np.array(_outs)[top_index])

#     return final_output[0] if len(final_output) == 1 else final_output
