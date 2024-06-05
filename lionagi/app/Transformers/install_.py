import subprocess
from lionagi.os.libs.sys_util import (
    install_import,
    get_cpu_architecture,
    is_package_installed,
)


def get_pytorch_install_command():
    cpu_arch = get_cpu_architecture()

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
    if not is_package_installed("torch"):
        in_ = input(
            "PyTorch is required for transformers. Would you like to install it now? (y/n): "
        )
        if in_ == "y":
            install_pytorch()
    if not is_package_installed("transformers"):
        in_ = input(
            "transformers is required. Would you like to install it now? (y/n): "
        )
        if in_ == "y":
            install_import(package_name="transformers", import_name="pipeline")
