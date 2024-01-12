import csv
import binascii
from datetime import datetime
from dateutil import parser
import io
from typing import List, Union, Any, Optional
import unittest


def merge_sorted_lists(list1: List[int], list2: List[int]) -> List[int]:
    """Merge two sorted lists into one sorted list.

    Args:
        list1: The first sorted list.
        list2: The second sorted list.

    Returns:
        A merged and sorted list containing all elements from both input lists.

    Examples:
        >>> merge_sorted_lists([1, 3, 5], [2, 4, 6])
        [1, 2, 3, 4, 5, 6]
        >>> merge_sorted_lists([], [2, 4, 6])
        [2, 4, 6]
    """
    merged_list = []
    i, j = 0, 0
    while i < len(list1) and j < len(list2):
        if list1[i] < list2[j]:
            merged_list.append(list1[i])
            i += 1
        else:
            merged_list.append(list2[j])
            j += 1
    merged_list.extend(list1[i:])
    merged_list.extend(list2[j:])
    return merged_list