# async def _score(
#     sentence,
#     instruction=None,
#     score_range=(1, 10),
#     inclusive=True,
#     num_digit=0,
#     confidence_score=False,
#     reason=False,
#     retries=2,
#     delay=0.5,
#     backoff_factor=2,
#     default_value=None,
#     timeout=None,
#     branch_name=None,
#     system=None,
#     messages=None,
#     service=None,
#     sender=None,
#     llmconfig=None,
#     tools=None,
#     datalogger=None,
#     persist_path=None,
#     tool_manager=None,
#     **kwargs,
# ):
#     if "temperature" not in kwargs:
#         kwargs["temperature"] = 0.1

#     instruction = instruction or ""

#     branch = Branch(
#         name=branch_name,
#         system=system,
#         messages=messages,
#         service=service,
#         sender=sender,
#         llmconfig=llmconfig,
#         tools=tools,
#         datalogger=datalogger,
#         persist_path=persist_path,
#         tool_manager=tool_manager,
#     )

#     _template = ScoreTemplate(
#         sentence=sentence,
#         instruction=instruction,
#         score_range=score_range,
#         inclusive=inclusive,
#         num_digit=num_digit,
#         confidence_score=confidence_score,
#         reason=reason,
#     )

#     await func_call.rcall(
#         branch.chat,
#         form=_template,
#         retries=retries,
#         delay=delay,
#         backoff_factor=backoff_factor,
#         default=default_value,
#         timeout=timeout,
#         **kwargs,
#     )

#     return _template


# async def score(
#     sentence,
#     *,
#     num_instances=1,
#     instruction=None,
#     score_range=(1, 10),
#     inclusive=True,
#     num_digit=0,
#     confidence_score=False,
#     reason=False,
#     retries=2,
#     delay=0.5,
#     backoff_factor=2,
#     default_value=None,
#     timeout=None,
#     branch_name=None,
#     system=None,
#     messages=None,
#     service=None,
#     sender=None,
#     llmconfig=None,
#     tools=None,
#     datalogger=None,
#     persist_path=None,
#     tool_manager=None,
#     return_template=True,
#     **kwargs,
# ) -> ScoreTemplate | float:

#     async def _inner(i=0):
#         return await _score(
#             sentence=sentence,
#             instruction=instruction,
#             score_range=score_range,
#             inclusive=inclusive,
#             num_digit=num_digit,
#             confidence_score=confidence_score,
#             reason=reason,
#             retries=retries,
#             delay=delay,
#             backoff_factor=backoff_factor,
#             default_value=default_value,
#             timeout=timeout,
#             branch_name=branch_name,
#             system=system,
#             messages=messages,
#             service=service,
#             sender=sender,
#             llmconfig=llmconfig,
#             tools=tools,
#             datalogger=datalogger,
#             persist_path=persist_path,
#             tool_manager=tool_manager,
#             **kwargs,
#         )

#     if num_instances == 1:
#         _out = await _inner()
#         return _out if return_template else _out.answer

#     elif num_instances > 1:
#         _outs = await func_call.alcall(range(num_instances), _inner)
#         return _outs if return_template else np.mean([i.answer for i in _outs])
