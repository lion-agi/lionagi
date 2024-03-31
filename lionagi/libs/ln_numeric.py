import numpy as np
from queue import PriorityQueue
from typing import List, Callable, Tuple, Dict, Any


# Numerical Utilities
class NumericalUtils:
    @staticmethod
    def percentile(values: List[float], percentile: float) -> float:
        if not values:
            return 0
        return max(np.percentile(values, percentile), 0.1)

    @staticmethod
    def moving_average(values: List[float], window_size: int) -> float:
        if len(values) < window_size:
            return np.mean(values) if values else 0
        return max(np.mean(values[-window_size:]), 0.1)
