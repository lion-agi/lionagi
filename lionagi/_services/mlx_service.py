from ..utils.sys_util import install_import, is_package_installed, as_dict
from .base_service import BaseService


class MlXService(BaseService):
    def __init__(self, model="mlx-community/OLMo-7B-hf-4bit-mlx", **kwargs):
        
        if not is_package_installed('mlx_lm'):
            install_import(package_name='mlx_lm')
            
        from mlx_lm import load, generate
        super().__init__()
        
        model_, tokenizer = load(model, **kwargs)
        
        self.model_name = model
        self.model = model_
        self.tokenizer = tokenizer
        self.generate = generate
        
    async def serve_chat(self, messages, **kwargs):
        prompts = [as_dict(msg['content'])['instruction'] for msg in messages if msg['role'] == 'user']
        
        payload = {'messages': messages}
        
        try:
            response = self.generate(
                self.model, self.tokenizer, prompt=f"{prompts[-1]} \nOutput: ", **kwargs
            )
            completion = {
                'model': self.model_name, 
                'choices': [{'message': response}]
            }
            
            return payload, completion
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e
        