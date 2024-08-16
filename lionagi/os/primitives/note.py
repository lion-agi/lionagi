from typing import TypeAliasType
from lion_core.generic.note import Note, note as _note


note = TypeAliasType("note", Note)
note.__call__ = _note

__all__ = ["Note", "note"]
