# import os
# from api.apicore import _common as _common_


# @_common_.exception_handlers()
# def is_file_empty(filepath: str | None) -> bool:
#     """
#     Determines whether a specified file is empty.

#     This function checks if the file at the given filepath is empty by evaluating its size.
#     It first verifies that the file exists and is indeed a file, not a directory. Then it
#     checks the file's size. If the size is zero bytes, it returns True, indicating the file
#     is empty. Otherwise, it returns False.

#     Args:
#         filepath: The path of the file to be checked.

#     Returns:
#         bool: True if the file exists and is empty, False otherwise.

#     """
#     return os.path.getsize(filepath) == 0 if os.path.isfile(filepath) else False
