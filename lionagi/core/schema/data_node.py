from .mix_ins.data_node_mixin import DataNodeFromObjMixin, DataNodeToObjMixin


class DataNodeMixin(DataNodeFromObjMixin, DataNodeToObjMixin):
    pass


class DataNode(DataNodeMixin): ...
