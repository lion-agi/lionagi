from .coder.FileAnalyzer_prompt import FileAnalyzerPrompt as prompt
from .coder.FileAnalyzer_config import FileAnalyzerConfig as config
from lionagi.session.Session import Session, llmlog

# ToDo: make this into a class
# need to make a base class for all chains

def analyze_file(file: dict, _prompts: dict =prompt, _kwags: dict =config, verbose: bool =False):
    """
    Preliminary analysis of a file or chunk, LLM flow:
    1. init: initial reading and understanding the file (analyzer.initiate)
    2. summary: summarizing the file (analyzer.followup)
    3. design: design algorithm from the file content (analyzer.followup)
    4. validate: validate the algorithm design (validator.initiate)
    5. output: output the final summary and algorithm design (analyzer.followup)

    Args:
    1. file (dict): file or chunk as dict, with keys: folder, file, chunk_id, chunk_size, content
        
    2. _prompts (dict, optional): prompts to use for running the analyze function. Defaults to
        FileAnalyzer_prompt under config.coder. Need to include keys: system, initial, summary, design, validate, output.
        
    3. _kwags (dict, optional): Configuration dict for additional kwags to pass into LLM call. Defaults to FileAnalyzer_config under config.coder. Need to include keys: model, sleep, with other optional keys. For detailed kwags check lionagi.session.Session.
        
    4. verbose (bool, optional): whether to print out message for successful saving of llm logs to logs. Defaults to False.

    Returns:
        processed file still as dict with additional keys: initial, summary, algo, validation, output for each llm output.
    """
    
    if len(llmlog.log) > 0:
        llmlog.to_csv(verbose=False)
        
    analyzer = Session(_prompts['system'])
    validator = Session(_prompts['system'])
    
    def _analyze_file(context):
        _init = analyzer.initiate(instruction=_prompts['initial'], context=context, temperature=0.6, **_kwags)
        _summary = analyzer.followup(instruction=_prompts['summary'], temperature=0.5, **_kwags)
        _algo = analyzer.followup(instruction=_prompts['design'], temperature=0.7, **_kwags)
        return (_init, _summary, _algo)
        
    def _validate_file(context):
        _validation = validator.initiate(instruction=_prompts['validate'], context=context, temperature=0.4, **_kwags)
        return _validation
    
    context0 = {**file}
    _init, _summary, _algo = [str(i).replace("\n", " ") for i in _analyze_file(context0)]
    
    context1 = {**file,'summary': _summary,'algo': _algo}
    _validation = str(_validate_file(context1)).replace('\n', ' ')

    context2 = {"file_validation": _validation}
    _output = analyzer.followup(instruction=_prompts['output'], context=context2, temperature=0.6, **_kwags)
    
    llmlog.to_csv(verbose=verbose)
    context0['initial'] = _init
    context0['summary'] = _summary
    context0['algo'] = _algo
    context0['validation'] = _validation
    context0['output'] = _output
    
    return context0