from .chat import Chat
from .unit.predict import Predict
from .unit.plan import Plan
from .unit.score import Score
from .unit.act import Act
from .unit.select import Select


DIRECTIVE_MAPPING = {
    "chat": Chat,
    "plan": Plan,
    "predict": Predict,
    "score": Score,
    "act": Act,
    "select": Select,
}
