from typing import Union, Dict, Any
import subprocess

from ..utils.sys_util import install_import, get_cpu_architecture, is_package_installed
from .base_service import BaseService


def get_pytorch_install_command():
    cpu_arch = get_cpu_architecture()

    if cpu_arch == 'apple_silicon':
        return "pip install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu"
    else:
        # Default CPU installation
        return "pip install torch torchvision torchaudio"

def install_pytorch():
    command = get_pytorch_install_command()
    try:
        subprocess.run(command.split(), check=True)
        print("PyTorch installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install PyTorch: {e}")

class TransformersService(BaseService):
    def __init__(self, task: str = None, model: Union[str, Any] = None, config: Union[str, Dict, Any] = None, device='cpu', **kwargs):
        super().__init__()
        self.task = task
        self.model = model
        self.config = config
        try:
            from transformers import pipeline
            self.pipeline = pipeline
        except ImportError:
            try: 
                if not is_package_installed('torch'):
                    in_ = input("PyTorch is required for transformers. Would you like to install it now? (y/n): ")
                    if in_ == 'y':
                        install_pytorch()
                if not is_package_installed('transformers'):
                    in_ = input("transformers is required. Would you like to install it now? (y/n): ")
                    if in_ == 'y':
                        install_import(
                            package_name='transformers',
                            import_name='pipeline'
                        )
                    from transformers import pipeline
                    self.pipeline = pipeline
            except Exception as e:
                raise ImportError(f'Unable to import required module from transformers. Please make sure that transformers is installed. Error: {e}')
        
        self.pipe = self.pipeline(task=task, model=model, config=config, device=device, **kwargs)

    async def serve_chat(self, messages, **kwargs):
        if self.task:
            if self.task != 'conversational':
                raise ValueError(f"Invalid transformers pipeline task: {self.task}.")

        payload = {'messages': messages}
        conversation = self.pipe(str(messages), **kwargs)
            
        texts = conversation[-1]['generated_text']
        msgs = str(texts.split(']')[1:]).replace('\\n', '').replace("[\'", "").replace('\\', '')
        
        completion = {
                      "model": self.pipe.model,
                      "choices": [{
                          "message": msgs
                      }]
        }

        return payload, completion
    