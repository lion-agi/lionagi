from collections.abc import Callable

from lionagi.protocols._concepts import Manager

"""
experimental
"""


class OperationManager(Manager):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.registry: dict[str, Callable] = {}
        self.register_operations(*args, **kwargs)

    def register_operations(self, *args, **kwargs) -> None:
        operations = {}
        if args:
            operations = {i.__name__ for i in args if hasattr(i, "__name__")}
        operations.update(kwargs)
        self.registry.update(operations)
