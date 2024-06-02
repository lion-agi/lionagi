import asyncio
from typing import Any, Type, Mapping
import logging
import aiohttp
from aiocache import cached

async def upload_file_with_retry(
    http_session: aiohttp.ClientSession,
    url: str,
    file_path: str,
    param_name: str = "file",
    additional_data: Mapping[str, Any] = None,
    retries: int = 3,
) -> Any:
    """
    Uploads a file to a specified URL with a retry mechanism for handling failures.

    Args:
            http_session: The HTTP session object to use for making the request.
            url: The URL to which the file will be uploaded.
            file_path: The path to the file that will be uploaded.
            param_name: The name of the parameter expected by the server for the file upload.
            additional_data: Additional data to be sent with the upload.
            retries: The number of times to retry the upload in case of failure.

    Returns:
            The HTTP assistant_response object.

    Examples:
            >>> session = aiohttp.ClientSession()
            >>> assistant_response = await APIUtil.upload_file_with_retry(session, 'http://example.com/upload', 'path/to/file.txt')
            >>> assistant_response.status
            200
    """
    for attempt in range(retries):
        try:
            with open(file_path, "rb") as file:
                files = {param_name: file}
                additional_data = additional_data or {}
                async with http_session.post(
                    url, data={**files, **additional_data}
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            if attempt == retries - 1:
                raise e
            backoff = 2**attempt
            logging.info(f"Retrying {url} in {backoff} seconds...")
            await asyncio.sleep(backoff)
