"""unit directive"""

from .base import UnitDirective, Chat
from .predict import Predict
from .plan import Plan
from .score import Score
from .act import Act
from .select import Select


UNIT_DIRECTIVE_MAPPING = {
    "chat": Chat,
    "plan": Plan,
    "predict": Predict,
    "score": Score,
    "act": Act,
    "select": Select,
}


__all__ = [
    "UnitDirective",
    "Chat",
    "Predict",
    "Plan",
    "Score",
    "Act",
    "Select",
    "UNIT_DIRECTIVE_MAPPING",
]
