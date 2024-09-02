import subprocess
from lionagi.libs import SysUtil

from typing_extensions import deprecated

from lionagi.os.sys_utils import format_deprecated_msg


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.action.function_calling.FunctionCalling",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
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


def install_transformers():
    if not SysUtil.is_package_installed("torch"):
        in_ = input(
            "PyTorch is required for transformers. Would you like to install it now? (y/n): "
        )
        if in_ == "y":
            install_pytorch()
    if not SysUtil.is_package_installed("transformers"):
        in_ = input(
            "transformers is required. Would you like to install it now? (y/n): "
        )
        if in_ == "y":
            SysUtil.install_import(package_name="transformers", import_name="pipeline")
