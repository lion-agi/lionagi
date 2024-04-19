from lionagi.core.session.session import Session
from lionagi.lions.coder.interpreter.e2b import set_up_interpreter
from lionagi.lions.coder.util import extract_code_blocks, install_dependencies

coder_prompts = {
    "system": ...,
    "plan_code": ...,
    "write_code": ...,
    "review_code": ...,
    "modify_code": ...,
    "debug_code": ...,
}


class Coder:
    
    def __init__(self, prompts=None, session=None, session_kwargs={}, required_libraries=None) -> None:
        self.prompts = prompts or coder_prompts
        self.session = Session(system=self.prompts['system'], **session_kwargs) if not session else session
        self.required_libraries = required_libraries or ["lionagi"]

    async def _plan_code(self, context):
        plans = await self.session.chat(self.prompts["plan_code"], context=context)
        return plans

    async def _write_code(self, context=None):
        code = await self.session.chat(self.prompts["write_code"], context=context)
        return extract_code_blocks(code)
        
    async def _review_code(self, context=None):
        code = await self.session.chat(self.prompts["review_code"], context=context)
        return extract_code_blocks(code)
    
    async def _modify_code(self, context=None):
        code = await self.session.chat(self.prompts["modify_code"], context=context)
        return extract_code_blocks(code)
        
    async def _debug_code(self, context=None):
        code = await self.session.chat(self.prompts["debug_code"], context=context)
        return extract_code_blocks(code)
    
    def _handle_execution_error(self, execution, required_libraries=None):
        if execution.error and execution.error.name == 'ModuleNotFoundError':
            install_dependencies(required_libraries)
            return "try again"
        elif execution.error:
            return execution.error
    
    def execute_codes(self, code, **kwargs):
        interpreter = set_up_interpreter()
        with interpreter as sandbox:
            execution = sandbox.notebook.exec_cell(code, **kwargs)
            error = self._handle_execution_error(execution, required_libraries=kwargs.get('required_libraries'))
            if error == "try again":
                execution = sandbox.notebook.exec_cell(code, **kwargs)
            return execution


# task = '''
# write a pure python function that takes a list of integers and returns the sum of all the integers in the list. write a couple tests as well
# '''

# coder = Coder()
# plans = await coder._plan_code(task)
# code = await coder._write_code()
# execution = coder.execute_codes(code)