from lionagi._errors import OperationError


class FileError(OperationError):
    pass


class PathConstraintError(FileSystemError):
    """
    Error when path validation fails.
    Includes which constraint failed and why.
    """

    def __init__(
        self,
        path: Path,
        reason: str,
        pattern: Optional[str] = None,
        constraint: Optional[str] = None,
    ):
        self.reason = reason
        self.pattern = pattern
        self.constraint = constraint
        msg = f"Path constraint error for {path}: {reason}"
        if pattern:
            msg += f" (matched pattern: {pattern})"
        if constraint:
            msg += f" (failed constraint: {constraint})"
        super().__init__(msg, path)
