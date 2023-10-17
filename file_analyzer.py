from Session import Session, llmlog
from prompts.file_level import file_analysis_prompts
from config.file_config import file_analyzer_config


def analyze_file(_file, prompts=file_analysis_prompts, _kwags=file_analyzer_config, verbose=False):
    if len(llmlog.log) > 0:
        llmlog.to_csv(verbose=False)
        
    file_analyzer = Session(prompts[0])
    file_validator = Session(prompts[0])
    
    def _analyze_file(context):
        file_analyzer.initiate(instruction=prompts[1], context=context, temperature=0.6, **_kwags, out=False)
        file_summary = file_analyzer.followup(instruction=prompts[2], temperature=0.5, **_kwags)
        file_algo = file_analyzer.followup(instruction=prompts[3], temperature=0.7, **_kwags)
        return (file_summary, file_algo)
        
    def _validate_file(context):
        file_validation = file_validator.initiate(instruction=prompts[4], context=context, temperature=0.4, **_kwags)
        return file_validation
    
    context0 = {
        'folder': _file['folder'],
        'file': _file['file'],
        'chunk_id': _file['chunk_id'],
        'file_content': _file['content'],       
    }
    _summary, _algo = _analyze_file(context0)
    _summary = _summary.replace('\n', ' ')
    _algo = _algo.replace('\n', ' ')
    
    context1 = {
        'chunk': _file,
        'summary': _summary,
        'algo': _algo,
    }
    _validation = _validate_file(context1)
    _validation = _validation.replace('\n', ' ')
    
    context2 = {
        "file_validation": _validation
    }
    _output = file_analyzer.followup(instruction=prompts[5], context=context2, temperature=0.6, **_kwags)
    
    llmlog.to_csv(verbose=verbose)
    context0['summary'] = _summary
    context0['algo'] = _algo
    context0['validation'] = _validation
    context0['output'] = _output
    
    return context0