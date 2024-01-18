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
