from .chat import Chat
from .predict import Predict
from .plan import Plan
from .score import Score
from .act import Act
from .select import Select

from .ReAct import ReAct
from .followup import FollowUp


DIRECTIVE_MAPPING = {
    "ReAct": ReAct,
    "followup": FollowUp,
    "chat": Chat,
    "plan": Plan,
    "predict": Predict,
    "score": Score,
    "act": Act,
    "select": Select,
}
