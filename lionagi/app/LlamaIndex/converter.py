from lion_core.converter import Converter
from lionagi.os.libs import to_dict

from .utils import llama_meta_fields


class LlamaIndexNodeConverter(Converter):

    @staticmethod
    def from_obj(cls, obj, **kwargs) -> dict:
        dict_ = to_dict(obj, **kwargs)

        dict_["content"] = dict_.pop("text", None)
        metadata = dict_.pop("metadata", {})

        for field in llama_meta_fields:
            metadata[field] = dict_.pop(field, None)

        metadata["llama_index_class"] = metadata.pop("class_name", None)
        metadata["llama_index_id"] = metadata.pop("id_", None)
        metadata["llama_index_relationships"] = metadata.pop("relationships", None)
        dict_["metadata"] = metadata
        return dict_

    @staticmethod
    def to_obj(self, node_type="TextNode", **kwargs):
        from .textnode import to_llama_index_node

        dict_ = to_dict(self, **kwargs)
        return to_llama_index_node(node_type=node_type, **dict_)


class LlamaIndexPileLoader:

    def _llama_index_reader(
        reader,
        reader_args,
        reader_kwargs,
        load_args,
        load_kwargs,
        to_lion: bool | Callable,
    ):
        nodes = llama_index_read_data(
            reader, reader_args, reader_kwargs, load_args, load_kwargs
        )
        if isinstance(to_lion, bool) and to_lion is True:
            return pile([Node.from_llama_index(i) for i in nodes])

        elif isinstance(to_lion, Callable):
            nodes = _datanode_parser(nodes, to_lion)
        return nodes

    ...
