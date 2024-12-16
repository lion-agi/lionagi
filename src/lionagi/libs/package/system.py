import platform


def get_cpu_architecture() -> str:
    """
    Get the CPU architecture.

    Returns:
        str: 'arm64' if ARM-based, 'x86_64' for Intel/AMD 64-bit, or the
            actual architecture string for other cases.
    """
    arch: str = platform.machine().lower()
    if "arm" in arch or "aarch64" in arch:
        return "arm64"
    elif "x86_64" in arch or "amd64" in arch:
        return "x86_64"
    else:
        return arch
