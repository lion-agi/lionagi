from .endpoint_utils import call_api, create_payload
from ..llm_configs import oai_llmconfig, oai_schema



def handle_response(session, payload, completion):
    try:
        if "choices" in completion:
            session._logger({"input":payload, "output": completion})
            session.conversation.add_messages(response=completion['choices'][0])
            session.conversation.responses.append(session.conversation.messages[-1])
            session.conversation.response_counts += 1
            session.status_tracker.num_tasks_succeeded += 1
        else:
            session.status_tracker.num_tasks_failed += 1
                        
    except Exception as e:
        session.status_tracker.num_tasks_failed += 1
        raise e





    
    response = self.call_api()
    return self.process_response(response)





async def serve(session, endpoint,**kwargs):
    payload = create_payload(**kwargs)
    