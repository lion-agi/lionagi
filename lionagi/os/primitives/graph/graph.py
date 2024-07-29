from lion_core.graph.graph import Graph as CoreGraph

from ..node import Node


class Graph(CoreGraph, Node): ...


__all__ = ["Graph"]
