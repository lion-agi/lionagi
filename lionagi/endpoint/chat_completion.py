from .base_endpoint import BaseEndpoint


class ChatCompletion(BaseEndpoint):

    def create_payload(self, session,  schema, **kwargs):
        # currently only openai  are supported
        messages = session.conversation.messages
        config = {**session.llmconfig, **kwargs}
        
        payload = {"messages": messages}
        for key in schema['required']:
            payload.update({key: config[key]})

        for key in schema['optional']:
            if bool(config[key]) is True and str(config[key]).lower() != "none":
                payload.update({key: config[key]})
        return payload
    
    def process_response(self, session, payload, completion):
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