# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0
#
# Portions derived from  https://github.com/microsoft/autogen are under the MIT License.
# SPDX-License-Identifier: MIT


def transcribe_audio_file(file_path):
    """
    Transcribes the audio file located at the given file path.

    Args:
        file_path (str): The path to the audio file.

    Returns:
        str: The transcribed text from the audio file.
    """
    from .imports_utils import check_import

    whisper = check_import("whisper", pip_name="openai-whisper")

    model = whisper.load_model("base")
    result = model.transcribe(file_path)
    return result["text"]
