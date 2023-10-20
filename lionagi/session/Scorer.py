from .Session import Session
from lionagi.utils.sys_utils import str_to_num

ScorerConfig = {
    "model": "gpt-3.5-turbo-16k",
    "frequency_penalty": 0,
    "n": 1,
    "temperature": 1,
    "top_p": 1,
    "sleep": 0.1,
    "out": True
    }

class Scorer(Session):
    
    def __init__(self, system) -> None:
        super().__init__(system=system)
        self.config = ScorerConfig
        
    def _score(self, instruction, session, **kwags):
        
        config = {**self.config, **kwags}
        self.conversation.messages = session.conversation.messages
        self.conversation.change_system(self.conversation.system)
        self.conversation.add_messages(instruction=instruction)
        self.call_OpenAI_ChatCompletion(**config)
        
        score = str_to_num(self.conversation.responses[-1]['content'], 
                           upper_bound=100, lower_bound=1, _type=int)
        
        if isinstance(score, int):
            return score
        else: 
            raise ValueError(score)
    
    def score(self, instruction, session, num_tries=3, **kwags):

        for i in range(num_tries):
            try:
                return self._score(
                    instruction=instruction, 
                    session=session, **kwags)
            except ValueError as e:
                print(f"Error: {e}")
                print(f"Attempt {i+1} of {num_tries}")
                continue