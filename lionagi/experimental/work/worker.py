from abc import ABC, abstractmethod
from lionagi import logging as _logging
from .work_function import WorkFunction
import asyncio

class Worker(ABC):
    # This is a class that will be used to create a worker object
    # work_functions are keyed by assignment {assignment: WorkFunction}
    
    name: str = "Worker"
    work_functions: dict[str, WorkFunction] = {}
    
    def __init__(self) -> None:
        self.stopped = False
        
    async def stop(self):
        self.stopped = True
        _logging.info(f"Stopping worker {self.name}")
        non_stopped_ = []
        
        for func in self.work_functions.values():
            worklog = func.worklog
            await worklog.stop()
            if not worklog.stopped:
                non_stopped_.append(func.name)

        if len(non_stopped_) > 0:
            _logging.error(f"Could not stop worklogs: {non_stopped_}")
            
        _logging.info(f"Stopped worker {self.name}")


    async def process(self, refresh_time=1):
        while not self.stopped:
            tasks = [
                asyncio.create_task(func.process(refresh_time=refresh_time))
                for func in self.work_functions.values()
            ]
            await asyncio.wait(tasks)
            await asyncio.sleep(refresh_time)
            

# # Example
# from lionagi import Session
# from lionagi.experimental.work.work_function import work


# class MyWorker(Worker):
    
#     @work(assignment="instruction, context -> response")
#     async def chat(instruction=None, context=None):
#         session = Session()
#         return await session.chat(instruction=instruction, context=context)
    

# await a.chat(instruction="Hello", context={})