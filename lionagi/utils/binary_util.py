import csv
import binascii
from datetime import datetime
from dateutil import parser
import io
from typing import List, Union, Any, Optional
import unittest

# filename: _sys_util9.txt
import csv
import binascii
from datetime import datetime
from dateutil import parser
import io
import unittest

    
# filename: _sys_util12.txt
import hashlib
import re
from typing import Generator, Optional, Union, Type, List
import unittest


def binary_to_hex(data: bytes) -> str:
    """Convert binary data to a hexadecimal string representation.

    Args:
        data: A bytes object containing binary data.

    Returns:
        A string containing the hexadecimal representation of the binary data.

    Examples:
        >>> binary_to_hex(b'\x00\x0F')
        '000f'
        >>> binary_to_hex(b'hello')
        '68656c6c6f'
    """
    return binascii.hexlify(data).decode()


def create_hash(data: str, algorithm: str = 'sha256') -> str:
    """Create a hash of the given data using the specified algorithm.

    Args:
        data: The string to hash.
        algorithm: The hashing algorithm to use (default is 'sha256').

    Returns:
        The hexadecimal digest of the hash.

    Examples:
        >>> create_hash('hello')
        '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
    """
    hasher = hashlib.new(algorithm)
    hasher.update(data.encode())
    return hasher.hexdigest()
