import subprocess
from typing import Any, Dict, Union

from lionagi.libs.ln_api import BaseService
from lionagi.libs.sys_util import SysUtil

allowed_kwargs = [
    # "model",
    "tokenizer",
    "modelcard",
    "framework",
    "task",
    "num_workers",
    "batch_size",
    "args_parser",
    "device",
    "torch_dtype",
    "min_length_for_response",
    "minimum_tokens",
    "mask_token",
    "max_length",
    "max_new_tokens",
]


def get_pytorch_install_command():
    cpu_arch = SysUtil.get_cpu_architecture()

    if cpu_arch == "apple_silicon":
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
    def __init__(
        self,
        task: str = None,
        model: str | Any = None,
        config: str | dict | Any = None,
        device="cpu",
        **kwargs,
    ):
        super().__init__()
        self.task = task
        self.model = model
        self.config = config
        self.allowed_kwargs = allowed_kwargs
        try:
            from transformers import pipeline

            self.pipeline = pipeline
        except ImportError:
            try:
                if not SysUtil.is_package_installed("torch"):
                    install_pytorch()
                if not SysUtil.is_package_installed("transformers"):
                    SysUtil.install_import(
                        package_name="transformers", import_name="pipeline"
                    )
                    from transformers import pipeline

                    self.pipeline = pipeline
            except Exception as e:
                raise ImportError(
                    f"Unable to import required module from transformers. Please make sure that transformers is installed. Error: {e}"
                )

        self.pipe = self.pipeline(
            task=task, model=model, config=config, device=device, **kwargs
        )

    async def serve_chat(self, messages, **kwargs):
        if self.task:
            if self.task != "conversational":
                raise ValueError(
                    f"Invalid transformers pipeline task: {self.task}."
                )

        payload = {"messages": messages}
        config = {}
        for k, v in kwargs.items():
            if k == "max_tokens":
                config["max_new_tokens"] = v
            if k in allowed_kwargs:
                config[k] = v

        msg = "".join([i["content"] for i in messages if i["role"] == "user"])
        conversation = ""
        response = self.pipe(msg, **config)
        try:
            conversation = response[0]["generated_text"]
        except:
            conversation = response

        completion = {"choices": [{"message": {"content": conversation}}]}

        return payload, completion
