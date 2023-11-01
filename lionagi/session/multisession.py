from typing import Any, Callable, Dict, List, Optional
import asyncio

from ..utils.sys_utils import create_copies, l_call
from .configs import SessionConfig
from .session import Session

class MultiSession(SessionConfig):
    """
    Manages multiple parallel sessions of user-assistant interactions.
    For argument and method details, refer to the `Session` class.
    
    Attributes:
        num_conversation (int): Number of parallel sessions.
        sessions (List[Session]): List of individual Session objects.
    """

    def __init__(self, 
                 system: str, 
                 api_service: Callable, 
                 status_tracker: Callable, 
                 num: int = 3) -> None:
        """
        Initializes multiple parallel sessions.
        """
        
        super().__init__()
        self.num_conversation = num
        self.sessions = create_copies(
            Session(system=system, api_service=api_service, status_tracker=status_tracker), 
            n=num)
        
    def initiate(self, 
                 instruction: Dict[str, Any], 
                 system: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None, 
                 **kwargs) -> List[Any]:
        """
        Initiates a new conversation session or restarts an existing one for all sessions.
        """

        config = {**self.config, **kwargs}
        system = system if system else self.sessions[0].conversation.system

        def initiate_single_session(session):
            return session.initiate(
                instruction=instruction, 
                system=system, 
                context=context, **config
            )
        
        results = l_call(self.sessions, initiate_single_session)
    
        if config['out']:
            return results

    def followup(self, 
                 instruction: Dict[str, Any], 
                 system: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None, 
                 **kwargs) -> List[Any]:
        """
        Adds a follow-up instruction to an ongoing conversation for all sessions.
        """

        config = {**self.config, **kwargs}

        def followup_single_session(session):
            if system:
                session.conversation.change_system(system)
            return session.followup(
                system=system, 
                instruction=instruction, 
                context=context, **config
            )
        
        results = l_call(self.sessions, followup_single_session)
        
        if config['out']:
            return results


    async def ainitiate(self, 
                        instruction: Dict[str, Any], 
                        system: Optional[str] = None, 
                        context: Optional[Dict[str, Any]] = None, 
                        **kwargs) -> List[Any]:
        """
        Asynchronously initiates a new conversation session or restarts an existing one for all sessions.
        """
        
        config = {**self.config, **kwargs}
        system = system if system else self.sessions[0].conversation.system

        async def initiate_single_session(session):
            return await session.initiate(
                instruction=instruction, 
                system=system, 
                context=context, **config
            )
        
        results = await asyncio.gather(
            *[initiate_single_session(session) for session in self.sessions]
        )
        
        if config['out']:
            return results

    async def afollowup(self, 
                        instruction: Dict[str, Any], 
                        system: Optional[str] = None, 
                        context: Optional[Dict[str, Any]] = None, 
                        **kwargs) -> List[Any]:
        """
        Asynchronously adds a follow-up instruction to an ongoing conversation for all sessions.
        """

        config = {**self.config, **kwargs}

        async def followup_single_session(session):
            if system:
                session.conversation.change_system(system)
            return await session.followup(     
                system=system,       
                instruction=instruction, 
                context=context, **config)
        
        results = await asyncio.gather(
            *[followup_single_session(session) for session in self.sessions]
        )
        
        if config['out']:
            return results