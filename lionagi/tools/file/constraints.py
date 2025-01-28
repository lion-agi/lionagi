"""
Enhanced path constraints and validation.
Provides robust security checks with detailed error reporting.
"""

import os
import re
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Pattern, Set, Union

from .base_ import FileOperation, PathConstraintError


class SymlinkPolicy(str, Enum):
    """
    Granular symlink handling policies.
    """

    ALLOW = "allow"  # Allow all symlinks
    DENY = "deny"  # Deny all symlinks
    INTERNAL = "internal"  # Allow only if target in allowed paths
    RELATIVE = "relative"  # Allow only relative symlinks
    TARGET_CHECK = "check"  # Check target against constraints


class ExtensionPolicy(str, Enum):
    """
    File extension handling policies.
    """

    ALLOW_LISTED = "allow_listed"  # Only allow listed extensions
    BLOCK_LISTED = "block_listed"  # Block listed extensions
    UNRESTRICTED = "unrestricted"  # No extension restrictions


class PathConstraints:
    """
    Enhanced path validation with detailed policies and error reporting.

    Features:
    - Robust path containment using commonpath
    - Granular symlink policies
    - Extension validation
    - Size limits
    - Detailed error reporting
    """

    def __init__(
        self,
        allowed_paths: Optional[List[Union[str, Path]]] = None,
        blocked_patterns: Optional[List[str]] = None,
        allowed_extensions: Optional[List[str]] = None,
        blocked_extensions: Optional[List[str]] = None,
        extension_policy: ExtensionPolicy = ExtensionPolicy.UNRESTRICTED,
        symlink_policy: SymlinkPolicy = SymlinkPolicy.DENY,
        max_file_size: Optional[int] = None,
        max_path_length: Optional[int] = None,
    ):
        """
        Initialize path constraints.

        Args:
            allowed_paths: List of allowed root paths
            blocked_patterns: List of blocked path patterns
            allowed_extensions: List of allowed file extensions
            blocked_extensions: List of blocked file extensions
            extension_policy: How to handle extensions
            symlink_policy: How to handle symlinks
            max_file_size: Maximum file size in bytes
            max_path_length: Maximum path length
        """
        # Convert and validate paths
        self.allowed_paths: Set[Path] = set()
        if allowed_paths:
            for path in allowed_paths:
                resolved = Path(path).resolve()
                if not resolved.exists():
                    raise ValueError(f"Allowed path does not exist: {path}")
                self.allowed_paths.add(resolved)

        # Compile regex patterns
        self.blocked_patterns: List[Pattern] = []
        if blocked_patterns:
            for pattern in blocked_patterns:
                try:
                    self.blocked_patterns.append(re.compile(pattern))
                except re.error as e:
                    raise ValueError(f"Invalid regex pattern '{pattern}': {e}")

        # Extension policies
        self.extension_policy = extension_policy
        self.allowed_extensions = set(
            ext.lower().lstrip(".") for ext in (allowed_extensions or [])
        )
        self.blocked_extensions = set(
            ext.lower().lstrip(".") for ext in (blocked_extensions or [])
        )

        # Other constraints
        self.symlink_policy = symlink_policy
        self.max_file_size = max_file_size
        self.max_path_length = max_path_length

    def validate_path(
        self, path: Union[str, Path], operation: Optional[FileOperation] = None
    ) -> Path:
        """
        Validate path against all constraints.

        Args:
            path: Path to validate
            operation: Optional operation context

        Returns:
            Resolved Path object

        Raises:
            PathConstraintError: If any constraint fails
        """
        try:
            resolved = Path(path).resolve()
        except Exception as e:
            raise PathConstraintError(
                Path(path), f"Failed to resolve path: {e}"
            )

        # Path length check
        if self.max_path_length:
            path_len = len(str(resolved))
            if path_len > self.max_path_length:
                raise PathConstraintError(
                    resolved,
                    f"Path length {path_len} exceeds maximum {self.max_path_length}",
                    constraint="max_path_length",
                )

        # Allowed paths check
        if self.allowed_paths and not self._is_under_allowed_path(resolved):
            raise PathConstraintError(
                resolved,
                "Path not under any allowed root",
                constraint="allowed_paths",
            )

        # Blocked patterns check
        if pattern := self._matches_blocked_pattern(resolved):
            raise PathConstraintError(
                resolved,
                "Path matches blocked pattern",
                pattern=str(pattern.pattern),
                constraint="blocked_patterns",
            )

        # Extension check
        if not self._has_allowed_extension(resolved):
            raise PathConstraintError(
                resolved,
                "File extension not allowed",
                constraint="extension_policy",
            )

        # Symlink check
        if not self._check_symlink(resolved):
            raise PathConstraintError(
                resolved,
                f"Symlink not allowed (policy: {self.symlink_policy})",
                constraint="symlink_policy",
            )

        # Size check for existing files
        if operation != FileOperation.CREATE and resolved.exists():
            if not self._check_size(resolved):
                raise PathConstraintError(
                    resolved,
                    f"File size exceeds maximum {self.max_file_size} bytes",
                    constraint="max_file_size",
                )

        return resolved

    def _is_under_allowed_path(self, path: Path) -> bool:
        """
        Check if path is under an allowed root using commonpath.
        Handles cross-platform paths and edge cases.
        """
        if not self.allowed_paths:
            return True

        resolved = path.resolve()
        for allowed in self.allowed_paths:
            try:
                common = os.path.commonpath([resolved, allowed])
                if str(common) == str(allowed):
                    return True
            except ValueError:
                # Paths on different drives or incompatible
                continue
        return False

    def _matches_blocked_pattern(self, path: Path) -> Optional[Pattern]:
        """
        Check if path matches any blocked pattern.
        Returns the matching pattern if found.
        """
        path_str = str(path)
        for pattern in self.blocked_patterns:
            if pattern.search(path_str):
                return pattern
        return None

    def _has_allowed_extension(self, path: Path) -> bool:
        """Check file extension against policies."""
        ext = path.suffix.lower().lstrip(".")

        if self.extension_policy == ExtensionPolicy.UNRESTRICTED:
            return True

        if self.extension_policy == ExtensionPolicy.ALLOW_LISTED:
            return ext in self.allowed_extensions

        if self.extension_policy == ExtensionPolicy.BLOCK_LISTED:
            return ext not in self.blocked_extensions

        return True

    def _check_symlink(self, path: Path) -> bool:
        """
        Check symlink against policy.
        Handles different symlink scenarios.
        """
        if not path.is_symlink():
            return True

        if self.symlink_policy == SymlinkPolicy.ALLOW:
            return True

        if self.symlink_policy == SymlinkPolicy.DENY:
            return False

        target = Path(os.readlink(path))

        if self.symlink_policy == SymlinkPolicy.INTERNAL:
            # Check if target is under allowed paths
            return self._is_under_allowed_path(target)

        if self.symlink_policy == SymlinkPolicy.RELATIVE:
            # Only allow relative symlinks
            return not target.is_absolute()

        if self.symlink_policy == SymlinkPolicy.TARGET_CHECK:
            # Validate target against all constraints
            try:
                self.validate_path(target)
                return True
            except PathConstraintError:
                return False

        return False

    def _check_size(self, path: Path) -> bool:
        """Check file size against limit."""
        if not self.max_file_size:
            return True

        try:
            return path.stat().st_size <= self.max_file_size
        except OSError:
            # Can't check size, assume it's ok
            # Size will be checked during actual read/write
            return True
