E2B_key_scheme = "E2B_API_KEY"

def set_up_interpreter(interpreter_provider="e2b",key_scheme=E2B_key_scheme):
    
    if interpreter_provider == "e2b":
        from lionagi.libs import SysUtil
        SysUtil.check_import("e2b_code_interpreter")
        
        from e2b_code_interpreter import CodeInterpreter
        from os import getenv

        return CodeInterpreter(api_key=getenv(key_scheme))

    else:
        raise ValueError("Invalid interpreter provider")