from lion_core.communication.instruction import Instruction
from lion_core.session.branch import Branch
from typing_extensions import deprecated


@deprecated("Deprecated")
def has_tools(self: Branch) -> bool:
    """
    deprecated
    Checks if the branch has tools.

    Returns:
        bool: True if the branch has tools, else False.
    """
    return self.tool_manager.registry != {}


@deprecated("Deprecated")
def update_last_instruction_meta(self: Branch, meta):
    """
    deprecated
    Updates metadata of the last instruction.

    Args:
        meta (dict): The metadata to update.
    """
    for i in reversed(self.progress):
        if isinstance(self.messages[i], Instruction):
            self.messages[i].metadata.insert(["extra"], meta)
            return


deprecated_methods = {
    "has_tools": property(has_tools),
    "update_last_instruction_meta": update_last_instruction_meta,
}

for method_name, method in deprecated_methods.items():
    setattr(Branch, method_name, method)


__all__ = ["has_tools", "update_last_instruction_meta", Branch]
