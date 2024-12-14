# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0
#
# Portions derived from  https://github.com/microsoft/autogen are under the MIT License.
# SPDX-License-Identifier: MIT

import logging
import os
import pathlib
import re
import string
import subprocess
import sys
import time
import venv
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from hashlib import md5
from pathlib import Path
from types import SimpleNamespace


class _ModuleImportClass:

    from ..imports_utils import check_import

    docker = check_import("docker")
    DockerException = check_import(
        "docker.errors", import_name="DockerException"
    )
    ImageNotFound = check_import("docker.errors", import_name="ImageNotFound")


filename_patterns = [
    re.compile(r"^<!-- (filename:)?(.+?) -->", re.DOTALL),
    re.compile(r"^/\* (filename:)?(.+?) \*/", re.DOTALL),
    re.compile(r"^// (filename:)?(.+?)$", re.DOTALL),
    re.compile(r"^# (filename:)?(.+?)$", re.DOTALL),
]


# Raises ValueError if the file is not in the workspace
def _get_file_name_from_content(code: str, workspace_path: Path) -> str | None:
    first_line = code.split("\n")[0].strip()
    # TODO - support other languages
    for pattern in filename_patterns:
        matches = pattern.match(first_line)
        if matches is not None:
            filename = matches.group(2).strip()

            # Handle relative paths in the filename
            path = Path(filename)
            if not path.is_absolute():
                path = workspace_path / path
            path = path.resolve()
            # Throws an error if the file is not in the workspace
            relative = path.relative_to(workspace_path.resolve())
            return str(relative)
    return None


def silence_pip(code: str, lang: str) -> str:
    """Apply -qqq flag to pip install commands."""
    if lang == "python":
        regex = r"^! ?pip install"
    elif lang in ["bash", "shell", "sh", "pwsh", "powershell", "ps1"]:
        regex = r"^pip install"
    else:
        return code

    # Find lines that start with pip install and make sure "-qqq" flag is added.
    lines = code.split("\n")
    for i, line in enumerate(lines):
        # use regex to find lines that start with pip install.
        match = re.search(regex, line)
        if match is not None:
            if "-qqq" not in line:
                lines[i] = line.replace(
                    match.group(0), match.group(0) + " -qqq"
                )
    return "\n".join(lines)


SENTINEL = object()
DEFAULT_MODEL = "o1-mini"
FAST_MODEL = "gpt-4o-mini"
# Regular expression for finding a code block
# ```[ \t]*(\w+)?[ \t]*\r?\n(.*?)[ \t]*\r?\n``` Matches multi-line code blocks.
#   The [ \t]* matches the potential spaces before language name.
#   The (\w+)? matches the language, where the ? indicates it is optional.
#   The [ \t]* matches the potential spaces (not newlines) after language name.
#   The \r?\n makes sure there is a linebreak after ```.
#   The (.*?) matches the code itself (non-greedy).
#   The \r?\n makes sure there is a linebreak before ```.
#   The [ \t]* matches the potential spaces before closing ``` (the spec allows indentation).
CODE_BLOCK_PATTERN = r"```[ \t]*(\w+)?[ \t]*\r?\n(.*?)\r?\n[ \t]*```"
WORKING_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "extensions"
)
UNKNOWN = "unknown"
TIMEOUT_MSG = "Timeout"
DEFAULT_TIMEOUT = 600
WIN32 = sys.platform == "win32"
PATH_SEPARATOR = WIN32 and "\\" or "/"
PYTHON_VARIANTS = ["python", "Python", "py"]

logger = logging.getLogger(__name__)


def content_str(content) -> str:
    """Converts the `content` field of an OpenAI message into a string format.

    This function processes content that may be a string, a list of mixed text and image URLs, or None,
    and converts it into a string. Text is directly appended to the result string, while image URLs are
    represented by a placeholder image token. If the content is None, an empty string is returned.

    Args:
        - content (Union[str, List, None]): The content to be processed. Can be a string, a list of dictionaries
                                      representing text and image URLs, or None.

    Returns:
        str: A string representation of the input content. Image URLs are replaced with an image token.

    Note:
    - The function expects each dictionary in the list to have a "type" key that is either "text" or "image_url".
      For "text" type, the "text" key's value is appended to the result. For "image_url", an image token is appended.
    - This function is useful for handling content that may include both text and image references, especially
      in contexts where images need to be represented as placeholders.
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        raise TypeError(
            f"content must be None, str, or list, but got {type(content)}"
        )

    rst = ""
    for item in content:
        if not isinstance(item, dict):
            raise TypeError(
                "Wrong content format: every element should be dict if the content is a list."
            )
        assert (
            "type" in item
        ), "Wrong content format. Missing 'type' key in content's dict."
        if item["type"] == "text":
            rst += item["text"]
        elif item["type"] == "image_url":
            rst += "<image>"
        else:
            raise ValueError(
                f"Wrong content format: unknown type {item['type']} within the content"
            )
    return rst


def infer_lang(code: str) -> str:
    """infer the language for the code.
    TODO: make it robust.
    """
    if (
        code.startswith("python ")
        or code.startswith("pip")
        or code.startswith("python3 ")
    ):
        return "sh"

    # check if code is a valid python code
    try:
        compile(code, "test", "exec")
        return "python"
    except SyntaxError:
        # not a valid python code
        return UNKNOWN


# TODO: In the future move, to better support https://spec.commonmark.org/0.30/#fenced-code-blocks
#       perhaps by using a full Markdown parser.
def extract_code(
    text: str | list,
    pattern: str = CODE_BLOCK_PATTERN,
    detect_single_line_code: bool = False,
) -> list[tuple[str, str]]:
    """Extract code from a text.

    Args:
        text (str or List): The content to extract code from. The content can be
            a string or a list, as returned by standard GPT or multimodal GPT.
        pattern (str, optional): The regular expression pattern for finding the
            code block. Defaults to CODE_BLOCK_PATTERN.
        detect_single_line_code (bool, optional): Enable the new feature for
            extracting single line code. Defaults to False.

    Returns:
        list: A list of tuples, each containing the language and the code.
          If there is no code block in the input text, the language would be "unknown".
          If there is code block but the language is not specified, the language would be "".
    """
    text = content_str(text)
    if not detect_single_line_code:
        match = re.findall(pattern, text, flags=re.DOTALL)
        return match if match else [(UNKNOWN, text)]

    # Extract both multi-line and single-line code block, separated by the | operator
    # `([^`]+)`: Matches inline code.
    code_pattern = re.compile(CODE_BLOCK_PATTERN + r"|`([^`]+)`")
    code_blocks = code_pattern.findall(text)

    # Extract the individual code blocks and languages from the matched groups
    extracted = []
    for lang, group1, group2 in code_blocks:
        if group1:
            extracted.append((lang.strip(), group1.strip()))
        elif group2:
            extracted.append(("", group2.strip()))

    return extracted


def timeout_handler(signum, frame):
    raise TimeoutError("Timed out!")


def get_powershell_command():
    try:
        result = subprocess.run(
            ["powershell", "$PSVersionTable.PSVersion.Major"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return "powershell"
    except (FileNotFoundError, NotADirectoryError):
        # This means that 'powershell' command is not found so now we try looking for 'pwsh'
        try:
            result = subprocess.run(
                ["pwsh", "-Command", "$PSVersionTable.PSVersion.Major"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return "pwsh"
        except FileExistsError as e:
            raise FileNotFoundError(
                "Neither powershell.exe nor pwsh.exe is present in the system. "
                "Please install PowerShell and try again. "
            ) from e
        except NotADirectoryError as e:
            raise NotADirectoryError(
                "PowerShell is either not installed or its path is not given "
                "properly in the environment variable PATH. Please check the "
                "path and try again. "
            ) from e
    except PermissionError as e:
        raise PermissionError("No permission to run powershell.") from e


def _cmd(lang: str) -> str:
    if lang in PYTHON_VARIANTS:
        return "python"
    if lang.startswith("python") or lang in ["bash", "sh"]:
        return lang
    if lang in ["shell"]:
        return "sh"
    if lang == "javascript":
        return "node"
    if lang in ["ps1", "pwsh", "powershell"]:
        powershell_command = get_powershell_command()
        return powershell_command

    raise NotImplementedError(f"{lang} not recognized in code execution")


def is_docker_running() -> bool:
    """Check if docker is running.

    Returns:
        bool: True if docker is running; False otherwise.
    """
    try:
        client = _ModuleImportClass.docker.from_env()
        client.ping()
        return True
    except _ModuleImportClass.DockerException:
        return False


def in_docker_container() -> bool:
    """Check if the code is running in a docker container.

    Returns:
        bool: True if the code is running in a docker container; False otherwise.
    """
    return os.path.exists("/.dockerenv")


def decide_use_docker(use_docker: bool | None) -> bool | None:
    if use_docker is None:
        env_var_use_docker = os.environ.get("USE_DOCKER", "True")

        truthy_values = {"1", "true", "yes", "t"}
        falsy_values = {"0", "false", "no", "f"}

        # Convert the value to lowercase for case-insensitive comparison
        env_var_use_docker_lower = env_var_use_docker.lower()

        # Determine the boolean value based on the environment variable
        if env_var_use_docker_lower in truthy_values:
            use_docker = True
        elif env_var_use_docker_lower in falsy_values:
            use_docker = False
        elif (
            env_var_use_docker_lower == "none"
        ):  # Special case for 'None' as a string
            use_docker = None
        else:
            # Raise an error for any unrecognized value
            raise ValueError(
                f'Invalid value for AUTOGEN_USE_DOCKER: {env_var_use_docker}. Please set AUTOGEN_USE_DOCKER to "1/True/yes", "0/False/no", or "None".'
            )
    return use_docker


def check_can_use_docker_or_throw(use_docker) -> None:
    if use_docker is not None:
        inside_docker = in_docker_container()
        docker_installed_and_running = is_docker_running()
        if (
            use_docker
            and not inside_docker
            and not docker_installed_and_running
        ):
            raise RuntimeError(
                "Code execution is set to be run in docker (default behaviour) but docker is not running.\n"
                "The options available are:\n"
                "- Make sure docker is running (advised approach for code execution)\n"
                '- Set "use_docker": False in code_execution_config\n'
                '- Set AUTOGEN_USE_DOCKER to "0/False/no" in your environment variables'
            )


def _sanitize_filename_for_docker_tag(filename: str) -> str:
    """Convert a filename to a valid docker tag.
    See https://docs.docker.com/engine/reference/commandline/tag/ for valid tag
    format.

    Args:
        filename (str): The filename to be converted.

    Returns:
        str: The sanitized Docker tag.
    """
    # Replace any character not allowed with an underscore
    allowed_chars = set(string.ascii_letters + string.digits + "_.-")
    sanitized = "".join(
        char if char in allowed_chars else "_" for char in filename
    )

    # Ensure it does not start with a period or a dash
    if sanitized.startswith(".") or sanitized.startswith("-"):
        sanitized = "_" + sanitized[1:]

    # Truncate if longer than 128 characters
    return sanitized[:128]


def execute_code(
    code: str | None = None,
    timeout: int | None = None,
    filename: str | None = None,
    work_dir: str | None = None,
    use_docker: list[str] | str | bool = SENTINEL,
    lang: str | None = "python",
) -> tuple[int, str, str | None]:
    """Execute code in a docker container.
    This function is not tested on MacOS.

    Args:
        code (Optional, str): The code to execute.
            If None, the code from the file specified by filename will be executed.
            Either code or filename must be provided.
        timeout (Optional, int): The maximum execution time in seconds.
            If None, a default timeout will be used. The default timeout is 600 seconds. On Windows, the timeout is not enforced when use_docker=False.
        filename (Optional, str): The file name to save the code or where the code is stored when `code` is None.
            If None, a file with a randomly generated name will be created.
            The randomly generated file will be deleted after execution.
            The file name must be a relative path. Relative paths are relative to the working directory.
        work_dir (Optional, str): The working directory for the code execution.
            If None, a default working directory will be used.
            The default working directory is the "extensions" directory under
            "path_to_autogen".
        use_docker (list, str or bool): The docker image to use for code execution.
            Default is True, which means the code will be executed in a docker container. A default list of images will be used.
            If a list or a str of image name(s) is provided, the code will be executed in a docker container
            with the first image successfully pulled.
            If False, the code will be executed in the current environment.
            Expected behaviour:
                - If `use_docker` is not set (i.e. left default to True) or is explicitly set to True and the docker package is available, the code will run in a Docker container.
                - If `use_docker` is not set (i.e. left default to True) or is explicitly set to True but the Docker package is missing or docker isn't running, an error will be raised.
                - If `use_docker` is explicitly set to False, the code will run natively.
            If the code is executed in the current environment,
            the code must be trusted.
        lang (Optional, str): The language of the code. Default is "python".

    Returns:
        int: 0 if the code executes successfully.
        str: The error message if the code fails to execute; the stdout otherwise.
        image: The docker image name after container run when docker is used.
    """
    if all((code is None, filename is None)):
        error_msg = f"Either {code=} or {filename=} must be provided."
        logger.error(error_msg)
        raise AssertionError(error_msg)

    running_inside_docker = in_docker_container()
    docker_running = is_docker_running()

    # SENTINEL is used to indicate that the user did not explicitly set the argument
    if use_docker is SENTINEL:
        use_docker = decide_use_docker(use_docker=None)
    check_can_use_docker_or_throw(use_docker)

    timeout = timeout or DEFAULT_TIMEOUT
    original_filename = filename
    if WIN32 and lang in ["sh", "shell"] and (not use_docker):
        lang = "ps1"
    if filename is None:
        code_hash = md5(code.encode()).hexdigest()
        # create a file with a automatically generated name
        filename = f"tmp_code_{code_hash}.{'py' if lang.startswith('python') else lang}"
    if work_dir is None:
        work_dir = WORKING_DIR

    filepath = os.path.join(work_dir, filename)
    file_dir = os.path.dirname(filepath)
    os.makedirs(file_dir, exist_ok=True)

    if code is not None:
        with open(filepath, "w", encoding="utf-8") as fout:
            fout.write(code)

    if not use_docker or running_inside_docker:
        # already running in a docker container
        cmd = [
            sys.executable if lang.startswith("python") else _cmd(lang),
            f".\\{filename}" if WIN32 else filename,
        ]
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                subprocess.run,
                cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
            )
            try:
                result = future.result(timeout=timeout)
            except TimeoutError:
                if original_filename is None:
                    os.remove(filepath)
                return 1, TIMEOUT_MSG, None
        if original_filename is None:
            os.remove(filepath)
        if result.returncode:
            logs = result.stderr
            if original_filename is None:
                abs_path = str(pathlib.Path(filepath).absolute())
                logs = logs.replace(str(abs_path), "").replace(filename, "")
            else:
                abs_path = (
                    str(pathlib.Path(work_dir).absolute()) + PATH_SEPARATOR
                )
                logs = logs.replace(str(abs_path), "")
        else:
            logs = result.stdout
        return result.returncode, logs, None

    # create a docker client
    if use_docker and not docker_running:
        raise RuntimeError(
            "Docker package is missing or docker is not running. Please make sure docker is running or set use_docker=False."
        )

    client = _ModuleImportClass.docker.from_env()

    image_list = (
        ["python:3-slim", "python:3", "python:3-windowsservercore"]
        if use_docker is True
        else [use_docker] if isinstance(use_docker, str) else use_docker
    )
    for image in image_list:
        # check if the image exists
        try:
            client.images.get(image)
            break
        except _ModuleImportClass.ImageNotFound:
            # pull the image
            print("Pulling image", image)
            try:
                client.images.pull(image)
                break
            except _ModuleImportClass.DockerException:
                print("Failed to pull image", image)
    # get a randomized str based on current time to wrap the exit code
    exit_code_str = f"exitcode{time.time()}"
    abs_path = pathlib.Path(work_dir).absolute()
    cmd = [
        "sh",
        "-c",
        f'{_cmd(lang)} "{filename}"; exit_code=$?; echo -n {exit_code_str}; echo -n $exit_code; echo {exit_code_str}',
    ]
    # create a docker container
    container = client.containers.run(
        image,
        command=cmd,
        working_dir="/workspace",
        detach=True,
        # get absolute path to the working directory
        volumes={abs_path: {"bind": "/workspace", "mode": "rw"}},
    )
    start_time = time.time()
    while container.status != "exited" and time.time() - start_time < timeout:
        # Reload the container object
        container.reload()
    if container.status != "exited":
        container.stop()
        container.remove()
        if original_filename is None:
            os.remove(filepath)
        return 1, TIMEOUT_MSG, image
    # get the container logs
    logs = container.logs().decode("utf-8").rstrip()
    # commit the image
    tag = _sanitize_filename_for_docker_tag(filename)
    container.commit(repository="python", tag=tag)
    # remove the container
    container.remove()
    # check if the code executed successfully
    exit_code = container.attrs["State"]["ExitCode"]
    if exit_code == 0:
        # extract the exit code from the logs
        pattern = re.compile(f"{exit_code_str}(\\d+){exit_code_str}")
        match = pattern.search(logs)
        exit_code = 1 if match is None else int(match.group(1))
        # remove the exit code from the logs
        logs = logs if match is None else pattern.sub("", logs)

    if original_filename is None:
        os.remove(filepath)
    if exit_code:
        logs = logs.replace(
            f"/workspace/{filename if original_filename is None else ''}", ""
        )
    # return the exit code, logs and image
    return exit_code, logs, f"python:{tag}"


def create_virtual_env(dir_path: str, **env_args) -> SimpleNamespace:
    """Creates a python virtual environment and returns the context.

    Args:
        dir_path (str): Directory path where the env will be created.
        **env_args: Any extra args to pass to the `EnvBuilder`

    Returns:
        SimpleNamespace: the virtual env context object."""
    if not env_args:
        env_args = {"with_pip": True}
    env_builder = venv.EnvBuilder(**env_args)
    env_builder.create(dir_path)
    return env_builder.ensure_directories(dir_path)
