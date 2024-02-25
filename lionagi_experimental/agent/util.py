 #     tools = None,
    #     max_rounds: int = 1,

    #     fallback: Optional[Callable] = None,
    #     fallback_kwargs: Optional[Dict] = None,
    #     **kwargs
    # ):
    #     if tools is not None:
    #         if isinstance(tools, list) and isinstance(tools[0], Tool):
    #             self.register_tools(tools)

    #     if self.action_manager.registry == {}:
    #         raise ValueError("No tools found, You need to register tools for ReAct (reason-action)")

    #     else:
    #         kwargs = self.action_manager._tool_parser(tools=True, **kwargs)

    #     i = 0
    #     while i < max_rounds:
    #         prompt = f"""
    #             you have {(max_rounds-i)*2} step left in current task. reflect, perform
    #             reason for action plan according to available tools only, apply divide and conquer technique, retain from invoking functions
    #         """
    #         instruct = {"Notice": prompt}

    #         if i == 0:
    #             instruct["Task"] = instruction
    #             await self.chat(
    #                 instruction=instruct, context=context,
    #                 system=system, out=False, sender=sender, **kwargs
    #             )

    #         elif i >0:
    #             await self.chat(
    #                 instruction=instruct, out=False, sender=sender, **kwargs
    #             )

    #         prompt = f"""
    #             you have {(max_rounds-i)*2-1} step left in current task, invoke tools usage to perform the action
    #         """
    #         await self.chat(prompt, tool_choice="auto", tool_parsed=True, out=False,sender=sender, **kwargs)

    #         i += 1

    #     if self._is_invoked():
    #         if fallback is not None:
    #             if asyncio.iscoroutinefunction(fallback):
    #                 return await fallback(**fallback_kwargs)
    #             else:
    #                 return fallback(**fallback_kwargs)
    #         prompt = """
    #             present the final result to user
    #         """
    #         return await self.chat(prompt, sender=sender, tool_parsed=True, **kwargs)

    # from .sessions import Session

    # def get_config(temperature, max_tokens, key_scheme, n):
    #     f = lambda i:{
    #         "temperature": temperature[i],
    #         "max_tokens": max_tokens[i],
    #     }
    #     return {
    #         "key": f"{key_scheme}{n+1}",
    #         "config": f(n)
    #         }

    # async def run_workflow(
    #     session, prompts, temperature, max_tokens,
    #     key_scheme, num_prompts, context
    # ):
    #     for i in range(num_prompts):
    #         key_, config_ = get_config(temperature, max_tokens, key_scheme, i)
    #         if i == 0:
    #             await session.initiate(instruction=prompts[key_], context=context, **config_)
    #         else:
    #             await session.followup(instruction=prompts[key_], **config_)

    #         return session

    # async def run_auto_workflow(
    #     session, prompts, temperature, max_tokens,
    #     key_scheme, num_prompts, context
    # ):
    #     for i in range(num_prompts):
    #         key_, config_ = get_config(temperature, max_tokens, key_scheme, i)
    #         if i == 0:
    #             await session.initiate(instruction=prompts[key_], context=context, **config_)
    #         else:
    #             await session.auto_followup(instruction=prompts[key_], **config_)

    #         return session

    # async def run_session(
    #     prompts, dir, llmconfig, key_scheme, num_prompts,
    #     temperature, max_tokens, type_=None, tools=None
    # ):
    #     prompts_ = prompts.copy()
    #     session = Session(
    #         system=prompts_.pop('system', 'You are a helpful assistant'),
    #         dir = dir,
    #         llmconfig = llmconfig
    #     )
    #     if tools:
    #         session.register_tools(tools)
    #     if type_ is None:
    #         session = await run_workflow(
    #             session, prompts_, temperature, max_tokens,
    #             key_scheme=key_scheme, num_prompts=num_prompts
    #             )
    #     elif type_ == 'auto':
    #         session = await run_auto_workflow(
    #             session, prompts_, temperature, max_tokens,
    #             key_scheme=key_scheme, num_prompts=num_prompts
    #             )

    #     return session

    # async def followup(
    #     self,
    #     instruction: Union[Instruction, str],
    #     context = None,
    #     sender = None,
    #     system = None,
    #     tools: Union[bool, Tool, List[Tool], str, List[str], List[Dict]] = False,
    #     max_followup: int = 3,
    #     out=True,
    #     **kwargs
    # ) -> None:

    #     """
    #     auto Tool usages until LLM decides done. Then presents final results.
    #     """

    #     if self.action_manager.registry != {} and tools:
    #         kwargs = self.action_manager._BaseActionNode_parser(tools=tools, **kwargs)

    #     n_tries = 0
    #     while (max_followup - n_tries) > 0:
    #         prompt = f"""
    #             In the current task you are allowed a maximum of another {max_followup-n_tries} followup chats.
    #             if further tools are needed, invoke tools usage. If you are done, present the final result
    #             to user without further Tool usage.
    #         """
    #         if n_tries > 0:
    #             _out = await self.chat(prompt, sender=sender, BaseActionNode_choice="auto", BaseActionNode_parsed=True, **kwargs)
    #             n_tries += 1

    #             if not self._is_invoked():
    #                 return _out if out else None

    #         elif n_tries == 0:
    #             instruct = {"notice": prompt, "task": instruction}
    #             out = await self.chat(
    #                 instruct, context=context, system=system, sender=sender, BaseActionNode_choice="auto",
    #                 BaseActionNode_parsed=True, **kwargs
    #             )
    #             n_tries += 1

    #             if not self._is_invoked():
    #                 return _out if out else None

    # async def auto_ReAct(
    #     self,
    #     instruction: Union[Instruction, str],
    #     context = None,
    #     sender = None,
    #     system = None,
    #     tools = None,
    #     max_rounds: int = 1,

    #     fallback: Optional[Callable] = None,
    #     fallback_kwargs: Optional[Dict] = None,
    #     **kwargs
    # ):
    #     if tools is not None:
    #         if isinstance(tools, list) and isinstance(tools[0], Tool):
    #             self.register_BaseActionNodes(tools)

    #     if self.action_manager.registry == {}:
    #         raise ValueError("No tools found, You need to register tools for ReAct (reason-action)")

    #     else:
    #         kwargs = self.action_manager._BaseActionNode_parser(tools=True, **kwargs)

    #     i = 0
    #     while i < max_rounds:
    #         prompt = f"""
    #             you have {(max_rounds-i)*2} step left in current task. reflect, perform
    #             reason for action plan according to available tools only, apply divide and conquer technique, retain from invoking functions
    #         """
    #         instruct = {"Notice": prompt}

    #         if i == 0:
    #             instruct["Task"] = instruction
    #             await self.chat(
    #                 instruction=instruct, context=context,
    #                 system=system, out=False, sender=sender, **kwargs
    #             )

    #         elif i >0:
    #             await self.chat(
    #                 instruction=instruct, out=False, sender=sender, **kwargs
    #             )

    #         prompt = f"""
    #             you have {(max_rounds-i)*2-1} step left in current task, invoke Tool usage to perform the action
    #         """
    #         await self.chat(prompt, BaseActionNode_choice="auto", BaseActionNode_parsed=True, out=False,sender=sender, **kwargs)

    #         i += 1

    #     if self._is_invoked():
    #         if fallback is not None:
    #             if asyncio.iscoroutinefunction(fallback):
    #                 return await fallback(**fallback_kwargs)
    #             else:
    #                 return fallback(**fallback_kwargs)
    #         prompt = """
    #             present the final result to user
    #         """
    #         return await self.chat(prompt, sender=sender, BaseActionNode_parsed=True, **kwargs)

# from .sessions import Session

# def get_config(temperature, max_tokens, key_scheme, num):
#     f = lambda i:{
#         "temperature": temperature[i],
#         "max_tokens": max_tokens[i],
#     }
#     return {
#         "key": f"{key_scheme}{num+1}",
#         "config": f(num)
#         }

# async def run_workflow(
#     session, prompts, temperature, max_tokens,
#     key_scheme, num_prompts, context
# ):
#     for i in range(num_prompts):
#         key_, config_ = get_config(temperature, max_tokens, key_scheme, i)
#         if i == 0:
#             await session.initiate(instruction=prompts[key_], context=context, **config_)
#         else:
#             await session.followup(instruction=prompts[key_], **config_)

#         return session

# async def run_auto_workflow(
#     session, prompts, temperature, max_tokens,
#     key_scheme, num_prompts, context
# ):
#     for i in range(num_prompts):
#         key_, config_ = get_config(temperature, max_tokens, key_scheme, i)
#         if i == 0:
#             await session.initiate(instruction=prompts[key_], context=context, **config_)
#         else:
#             await session.auto_followup(instruction=prompts[key_], **config_)

#         return session

# async def run_session(
#     prompts, directory, llmconfig, key_scheme, num_prompts,
#     temperature, max_tokens, type_=None, tools=None
# ):
#     prompts_ = prompts.copy()
#     session = Session(
#         system=prompts_.pop('system', 'You are a helpful assistant'),
#         directory = directory,
#         llmconfig = llmconfig
#     )
#     if tools:
#         session.register_BaseActionNodes(tools)
#     if type_ is None:
#         session = await run_workflow(
#             session, prompts_, temperature, max_tokens,
#             key_scheme=key_scheme, num_prompts=num_prompts
#             )
#     elif type_ == 'auto':
#         session = await run_auto_workflow(
#             session, prompts_, temperature, max_tokens,
#             key_scheme=key_scheme, num_prompts=num_prompts
#             )

#     return session
