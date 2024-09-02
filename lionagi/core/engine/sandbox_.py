# filename: enhanced_script_engine.py
import ast

from typing_extensions import deprecated

from lionagi.os.sys_utils import format_deprecated_msg


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.action.function_calling.FunctionCalling",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
class SandboxTransformer(ast.NodeTransformer):
    """AST transformer to enforce restrictions in sandbox mode."""

    def visit_Import(self, node):
        raise RuntimeError("Import statements are not allowed in sandbox mode.")

    def visit_Exec(self, node):
        raise RuntimeError("Exec statements are not allowed in sandbox mode.")

    # Add other visit methods for disallowed operations or nodes
