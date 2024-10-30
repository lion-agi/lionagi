import os
import sys
from contextlib import asynccontextmanager

# import builtins
# import traceback

# original_print = builtins.print


# def new_print(*args, **kwargs):
#     # Get the last frame in the stack
#     frame = traceback.extract_stack(limit=2)[0]
#     # Insert the filename and line number
#     original_print(f"Called from {frame.filename}:{frame.lineno}")
#     # Call the original print
#     original_print(*args, **kwargs)


# Replace the built-in print with the new print
# builtins.print = new_print


@asynccontextmanager
async def async_suppress_print():
    """
    An asynchronous context manager that redirects stdout to /dev/null to suppress print output.
    """
    original_stdout = (
        sys.stdout
    )  # Save the reference to the original standard output
    with open(os.devnull, "w") as devnull:
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = original_stdout  # Restore standard output to the original value
