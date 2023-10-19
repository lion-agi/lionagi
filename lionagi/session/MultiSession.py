import asyncio
import numpy as np
from .Session import Session
from .Scorer import Scorer

class MultiSession:
    
    def __init__(self, system, num=3) -> None:
        self.system = system
        self.num_conversation = num
        self.sessions = [Session(system) for _ in range(num)]
        
    async def initiate(self, 
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
        
        async def initiate_single_session(session):
            return await session.initiate(
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
        
        results = await asyncio.gather(
            *[initiate_single_session(session) for session in self.sessions]
        )
        
        if out:
            return results

    async def followup(self,
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

        async def followup_single_session(session):
            return await session.followup(     
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
        
        results = await asyncio.gather(
            *[followup_single_session(session) for session in self.sessions]
        )
        
        if out:
            return results

    async def _score(self,
            score_system,
            score_instruction,
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
            num_tries=3):
        
        async def score_single_session(session):
            scorer = Scorer(score_system)
            return await scorer.score(
                instruction=score_instruction, 
                session=session,  
                model=model, 
                frequency_penalty=frequency_penalty, 
                function_call=function_call,
                functions=functions, 
                n=n,
                stop=stop,
                stream=stream,
                temperature=temperature,
                top_p=top_p, 
                sleep=sleep, 
                num_tries=num_tries)
        
        scores = await asyncio.gather(
            *[score_single_session(session) for session in self.sessions]
        )
        
        # Convert non-integer scores to 1
        return [score if isinstance(score, int) else 1 for score in scores]
    
    async def get_best_response(self, score_system=None, score_instruction=None):
        try: 
            scores = np.array(await self._score(score_system=score_system, score_instruction=score_instruction))
            return self.sessions[np.argmax(scores)].conversation.responses[-1]['content']
        except Exception as e:
            raise e
