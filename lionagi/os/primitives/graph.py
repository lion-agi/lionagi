from lion_core.graph.graph import Graph as CoreGraph
from lionagi.os.primitives.node import Node


class Graph(CoreGraph, Node):
    pass


__all__ = ["Graph"]
