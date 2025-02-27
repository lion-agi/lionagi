from .synthlang_.base import SynthlangFramework, SynthlangTemplate
from .synthlang_.translate_to_synthlang import translate_to_synthlang

# backwards compatibility
__all__ = (
    "translate_to_synthlang",
    "SynthlangFramework",
    "SynthlangTemplate",
)
