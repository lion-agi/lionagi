from .coder.BinAnalyzer_prompts import binprompts
from lionagi.session.Session import Session, llmlog
from timeit import default_timer as timer

def analyze_bin(_bin: dict, _prompts: dict=binprompts, verbose: bool=False, model="gpt-4", sleep=0.2):
    
    start = timer()
    if len(llmlog.log) > 0:
        llmlog.to_csv()
    
    a = Session(_prompts['system'])
    b = Session(_prompts['system'])
    
    def _analyze_bin(context): 
        _init = a.initiate(instruction=_prompts['initial'], context=context, temperature=0.75, model=model, sleep=sleep)
        _out1 = a.followup(instruction=_prompts['understand'], temperature=0.6, model=model, sleep=sleep)
        _out2 = a.followup(instruction=_prompts['plan'], temperature=0.7, model=model, sleep=sleep)
        _out3 = a.followup(instruction=_prompts['self_evaluation'], temperature=0.5, model=model, sleep=sleep)
        return (_init, _out1, _out2, _out3)

    def validate_bin(context):
        _validation = b.initiate(instruction=_prompts['validate'], context=context, temperature=0.4, model=model, sleep=sleep)
        return _validation
    
    def output_bin(context):
        _output = a.followup(instruction=_prompts['final'], context=context, temperature=0.6, model=model, sleep=sleep)
        return _output


    context0 = {**_bin}
    _init, _out1, _out2, _out3 = [str(i).replace("\n", " ") for i in _analyze_bin(context0)]
    
    context1 = {**_bin, 'understand': _out1, 'plan': _out2, "self_evaluation": _out3}
    _validation = str(validate_bin(context1)).replace('\n', ' ')

    context2 = {"bin_validation": _validation}
    _output = output_bin(context2)
    end = timer()
    
    llmlog.to_csv(verbose=verbose)
    context0['datetime'] = llmlog._get_timestamp()
    context0['chain_name'] = 'BinAnalyzer'
    context0['chain_version'] = '0.01'
    context0['chain_steps'] = 6
    context0['chian_runtime'] = end - start
    
    context0['session_1'] = 'analyzer'
    context0['session_1_system'] = _prompts['system']
    context0['session_2'] = 'validator'
    context0['session_2_system'] = _prompts['system']
    
    context0['step_1_model'] = model
    context0['step_1_name'] = 'initial'
    context0['step_1_session'] = 1
    context0['step_1_session_type'] = 'initiate'
    context0['step_1_prompt'] = _prompts['initial']
    context0['step_1_output'] = _init
    context0['step_1_context'] = 'all bin level info'
    
    context0['step_2_model'] = model 
    context0['step_2_name'] = 'understand'
    context0['step_2_session'] = 1
    context0['step_2_session_type'] = 'followup'
    context0['step_2_prompt'] = _prompts['understand']
    context0['step_2_output'] = _out1
    context0['step_2_context'] = None
    
    context0['step_3_model'] = model
    context0['step_3_name'] = 'plan'
    context0['step_3_session'] = 1
    context0['step_3_session_type'] = 'followup'
    context0['step_3_prompt'] = _prompts['plan']
    context0['step_3_output'] = _out2
    context0['step_3_context'] = None 
     
    context0['step_4_model'] = model 
    context0['step_4_name'] = 'self_evaluation'
    context0['step_4_session'] = 1
    context0['step_4_session_type'] = 'followup'
    context0['step_4_prompt'] = _prompts['self_evaluation']
    context0['step_4_output'] = _out3
    context0['step_4_context'] = None
    
    context0['step_5_model'] = model 
    context0['step_5_name'] = 'validate'
    context0['step_5_session'] = 2
    context0['step_5_session_type'] = 'initiate'
    context0['step_5_prompt'] = _prompts['validate']
    context0['step_5_output'] = _validation
    context0['step_5_context'] = ['step_1_context', 'step_2_output', 'step_3_output, step_4_output']

    context0['step_6_model'] = model 
    context0['step_6_name'] = 'final'
    context0['step_6_session'] = 1
    context0['step_6_session_type'] = 'followup'
    context0['step_6_prompt'] = _prompts['final']
    context0['step_6_output'] = _output
    context0['step_6_context'] = ['step_5_output']
    return context0
