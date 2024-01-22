"""async def critic_workflow():

    @ cd.max_concurrency(limit=3)
    async def run_critic_stage(critic_idx=None, step_num=None, outs=None, max_num_tool_uses=5):
        
        async def inner_func_():
            critic_ = f"critic{critic_idx}"
            name_ = li.nget(critics, [critic_, "name"])
            tool = li.nget(critics, [critic_, "tool"])
            instruction_ = li.nget(critics, [critic_, f"step{step_num}"])
            
            
            
            out = await researcher.auto_followup(branch=name_, instruction=instruction_, tools=tool, num=max_num_tool_uses)
            add_name_to_messages(name_)
            last_response = last_response_row(df=researcher.branches[name_].messages, name_=name_)
            outs.append(last_response)
            
            return out"""