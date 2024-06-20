from ..abc import Element, Field


class Event(Element):
    








from collections import defaultdict
from datetime import datetime
from typing import Callable, Dict, List, Any

class Event:
    def __init__(self, event_type: str, source: str, data: Any = None, priority: int = 0):
        self.type = event_type
        self.source = source
        self.timestamp = datetime.now()
        self.data = data if data is not None else {}
        self.priority = priority
        self.handled = False

    def mark_handled(self):
        self.handled = True

    def __repr__(self):
        return (f"Event(type={self.type}, source={self.source}, timestamp={self.timestamp}, "
                f"data={self.data}, priority={self.priority}, handled={self.handled})")
