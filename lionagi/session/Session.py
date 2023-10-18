from lionagi.utils.log_utils import llm_logger
import time
import openai
import json


llmlog = llm_logger()

# Messages Handling class - finished debugging
class Message:
    def __init__(self, role=None, content=None) -> None:
        self.role = role
        self.content = content

    def _create_message(self, system, response, instruction, context):
        if (system and (response or instruction)) or (response and instruction):
            return "Error: Message cannot have more than one role."
        else:
            if response:
                self.role = "assistant"
                self.content = response['content']
            elif instruction:
                self.role = "user"
                self.content = {"instruction": instruction}
                if context:
                    for key, item in context.items():
                        self.content[key] = item
            elif system:
                self.role = "system"
                self.content = system

    def to_dict(self, system=None, response=None, instruction=None, context=None):
        self._create_message(system=system, response=response, 
                             instruction=instruction, context=context)
        if self.role == "assistant":
            return {"role": self.role, "content": self.content}
        else:
            return {"role": self.role, "content": json.dumps(self.content)}

# Conversation Handling class - finished debugging
class Conversation:
    response_counts = 0
    def __init__(self, system, messages=[]) -> None:
        self.messages = messages
        self.system = system
        self.responses = []
        self.message = Message()

    def initiate_conversation(self, system, instruction, context=None):
        self.messages = []
        self.add_messages(system=system)
        self.add_messages(instruction=instruction, context=context)

    def add_messages(self, system=None, instruction=None, context=None, response=None):
        message = self.message.to_dict(
            system=system, 
            response=response, 
            instruction=instruction, 
            context=context)
        self.messages.append(message)
    
    def change_system(self, system):
        self.system = system
        self.messages[0] = self.message.to_dict(system=system)

    def get_OpenAI_ChatCompletion(self, model, 
                frequency_penalty=0, 
                function_call=None,
                functions=None, 
                n=1,
                stop=None,
                stream=False,
                temperature=1,
                top_p=1, 
                sleep=0.1):
        completion = ""
        messages = self.messages
        if (stream and (function_call or functions)):
            completion = openai.ChatCompletion.create(
                messages=messages,
                model=model,
                frequency_penalty=frequency_penalty,
                function_call=function_call,
                functions=functions,
                n=n,
                stop=stop,
                stream=True,
                temperature=temperature,
                top_p=top_p)
            completion = completion.choices[0]            
        elif stream:
            completion = openai.ChatCompletion.create(
                messages=messages,
                model=model,
                frequency_penalty=frequency_penalty,
                n=n,
                stop=stop,
                stream=True,
                temperature=temperature,
                top_p=top_p)
            completion = completion.choices[0]
        elif function_call or functions:
            completion = openai.ChatCompletion.create(
                messages=messages,
                model=model,
                frequency_penalty=frequency_penalty,
                function_call=function_call,
                functions=functions,
                n=n,
                stop=stop,
                temperature=temperature,
                top_p=top_p)
            completion = completion.choices[0]
        else:
            completion = openai.ChatCompletion.create(
                messages=messages,
                model=model,
                frequency_penalty=frequency_penalty,
                n=n,
                stop=stop,
                temperature=temperature,
                top_p=top_p)
            completion = completion.choices[0]
        response = {"role": "assistant", "content": completion.message['content']}
        self.responses.append(response)
        llmlog(self.messages, completion)
        self.response_counts += 1
        time.sleep(sleep)
    
    def append_last_response(self):
        self.add_messages(response=self.responses[-1])


class Session:
    
    def __init__(self, system) -> None:
        self.conversation = Conversation(system=system)

    def initiate(self, 
            instruction, 
            system=None, 
            context=None, 
            model="gpt-3.5-turbo-16k", 
            frequency_penalty=0, 
            function_call=None,
            functions=None, 
            n=1,
            stop=None,
            stream=False,
            temperature=1,
            top_p=1, 
            sleep=0.1, out=True):
        system = system if system else self.conversation.system
        self.conversation.initiate_conversation(system, instruction, context)
        self.conversation.get_OpenAI_ChatCompletion(
            model=model, 
            frequency_penalty=frequency_penalty, 
            function_call=function_call,
            functions=functions, 
            n=n,
            stop=stop,
            stream=stream,
            temperature=temperature,
            top_p=top_p, 
            sleep=sleep)
        if out:
            return self.conversation.responses[-1]['content']

    def followup(self,
            instruction,
            system=None, 
            context=None, 
            model="gpt-3.5-turbo-16k", 
            frequency_penalty=0, 
            function_call=None,
            functions=None, 
            n=1,
            stop=None,
            stream=False,
            temperature=1,
            top_p=1, 
            sleep=0.1, 
            out=True):
        self.conversation.append_last_response()
        if system:
            self.conversation.change_system(system)
        self.conversation.add_messages(instruction=instruction, context=context)
        self.conversation.get_OpenAI_ChatCompletion(
            model=model, 
            frequency_penalty=frequency_penalty, 
            function_call=function_call,
            functions=functions, 
            n=n,
            stop=stop,
            stream=stream,
            temperature=temperature,
            top_p=top_p, 
            sleep=sleep)
        if out:
            return self.conversation.responses[-1]['content']



# ToDo: finish scoring system

class MultiSession:
    
    def __init__(self, system, num=3) -> None:
        self.system = system
        self.num_conversation = num
        self.sessions = [Session(system) for _ in range(num)]
        
    def initiate(self, 
            instruction, 
            system=None, 
            context=None, 
            model="gpt-3.5-turbo-16k", 
            frequency_penalty=0, 
            function_call=None,
            functions=None, 
            n=1,
            stop=None,
            stream=False,
            temperature=1,
            top_p=1, 
            sleep=0.1, out=True):
        for session in self.sessions:        
            session.initiate(
                system=system,              
                instruction=instruction, 
                context=context,
                model=model, 
                frequency_penalty=frequency_penalty, 
                function_call=function_call,
                functions=functions, 
                n=n,
                stop=stop,
                stream=stream,
                temperature=temperature,
                top_p=top_p, 
                sleep=sleep)
        if out:
            return ([session.conversation.responses[-1]['content'] 
                     for session in self.sessions])

    def followup(self,
            instruction,
            system=None, 
            context=None, 
            model="gpt-3.5-turbo-16k", 
            frequency_penalty=0, 
            function_call=None,
            functions=None, 
            n=1,
            stop=None,
            stream=False,
            temperature=1,
            top_p=1, 
            sleep=0.1, 
            out=True):
        self.conversation.append_last_response()
        for session in self.sessions:        
            session.followup(     
                system=system,       
                instruction=instruction, 
                context=context,
                model=model, 
                frequency_penalty=frequency_penalty, 
                function_call=function_call,
                functions=functions, 
                n=n,
                stop=stop,
                stream=stream,
                temperature=temperature,
                top_p=top_p, 
                sleep=sleep)
        if out:
            return ([session.conversation.responses[-1]['content'] 
                     for session in self.sessions])
            
    # def _score(self,
    #         score_system,
    #         score_instruction,
    #         model="gpt-3.5-turbo-16k", 
    #         frequency_penalty=0, 
    #         function_call=None,
    #         functions=None, 
    #         n=1,
    #         stop=None,
    #         stream=False,
    #         temperature=1,
    #         top_p=1, 
    #         sleep=0.1, 
    #         num_tries=3):
    #     scorer = Scorer(score_system)
    #     scores = []
    #     for session in self.sessions:
    #         score = scorer.score(
    #             instruction=score_instruction, 
    #             session=session,  
    #             model=model, 
    #             frequency_penalty=frequency_penalty, 
    #             function_call=function_call,
    #             functions=functions, 
    #             n=n,
    #             stop=stop,
    #             stream=stream,
    #             temperature=temperature,
    #             top_p=top_p, 
    #             sleep=sleep, 
    #             num_tries=num_tries)
    #         if isinstance(score, int):
    #             scores.append(score)
    #         else:
    #             scores.append(1)
    #     return scores
    
    # def get_best_response(self, score_system=None, score_instruction=None):
    #     try: 
    #         scores = np.array(self._score(score_system=score_system,score_instruction=score_instruction))
    #         return self.sessions[np.argmax(scores)].conversation.responses[-1]['content']
    #     except Exception as e:
    #         raise e