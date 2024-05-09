from functools import singledispatchmethod
from typing import Any, Type, TypeVar
from pydantic import Field, AliasChoices, BaseModel, ValidationError
from pandas import DataFrame, Series

from lionagi.libs import SysUtil, convert, ParseUtil, nested
from lionagi.integrations.bridge import LlamaIndexBridge, LangchainBridge

from .component import BaseComponent
from .condition import Condition
from .edge import Edge
from .relation import Relations
from .mailbox import MailBox

T = TypeVar("T")

class BaseNode(BaseComponent):
    """
    Base class for creating node models.

    Attributes:
        content (Any | None): The optional content of the node.
        metadata (dict[str, Any]): Additional metadata for the node.
    """

    content: Any | None = Field(
        default=None,
        validation_alias=AliasChoices("text", "page_content", "chunk_content", "data"),
        description="The optional content of the node.",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias="meta",
        description="Additional metadata for the node.",
    )

    @singledispatchmethod
    @classmethod
    def from_obj(cls, obj: Any, *args, **kwargs) -> T:
        """
        Create a node instance from an object.

        Args:
            obj (Any): The object to create the node from.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Raises:
            NotImplementedError: If the object type is not supported.
        """
        if not isinstance(obj, (dict, str, list, Series, DataFrame, BaseModel)):
            type_ = str(type(obj))
            if "llama_index" in type_:
                return cls.from_obj(obj.to_dict())
            elif "langchain" in type_:
                langchain_json = obj.to_json()
                langchain_dict = {
                    "lc_id": langchain_json["id"],
                    **langchain_json["kwargs"],
                }
                return cls.from_obj(langchain_dict)

        raise NotImplementedError(f"Unsupported type: {type(obj)}")

    @from_obj.register(dict)
    @classmethod
    def _from_dict(cls, obj: dict, *args, **kwargs) -> T:
        """
        Create a node instance from a dictionary.

        Args:
            obj (dict): The dictionary to create the node from.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            T: The created node instance.
        """
        return cls.model_validate(obj, *args, **kwargs)

    @from_obj.register(str)
    @classmethod
    def _from_str(cls, obj: str, *args, fuzzy_parse: bool = False, **kwargs) -> T:
        """
        Create a node instance from a JSON string.

        Args:
            obj (str): The JSON string to create the node from.
            *args: Additional positional arguments.
            fuzzy_parse (bool): Whether to perform fuzzy parsing.
            **kwargs: Additional keyword arguments.

        Returns:
            T: The created node instance.
        """
        obj = ParseUtil.fuzzy_parse_json(obj) if fuzzy_parse else convert.to_dict(obj)
        try:
            return cls.from_obj(obj, *args, **kwargs)
        except ValidationError as e:
            raise ValueError(f"Invalid JSON for deserialization: {e}") from e

    @from_obj.register(list)
    @classmethod
    def _from_list(cls, obj: list, *args, **kwargs) -> list[T]:
        """
        Create a list of node instances from a list of objects.

        Args:
            obj (list): The list of objects to create nodes from.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            list[T]: The list of created node instances.
        """
        return [cls.from_obj(item, *args, **kwargs) for item in obj]

    @from_obj.register(Series)
    @classmethod
    def _from_pd_series(
        cls, obj: Series, *args, pd_kwargs: dict | None = None, **kwargs
    ) -> T:
        """
        Create a node instance from a Pandas Series.

        Args:
            obj (Series): The Pandas Series to create the node from.
            *args: Additional positional arguments.
            pd_kwargs (dict | None): Additional keyword arguments for Pandas Series.
            **kwargs: Additional keyword arguments.

        Returns:
            T: The created node instance.
        """
        pd_kwargs = pd_kwargs or {}
        return cls.from_obj(obj.to_dict(**pd_kwargs), *args, **kwargs)

    @from_obj.register(DataFrame)
    @classmethod
    def _from_pd_dataframe(
        cls, obj: DataFrame, *args, pd_kwargs: dict | None = None, **kwargs
    ) -> list[T]:
        """
        Create a list of node instances from a Pandas DataFrame.

        Args:
            obj (DataFrame): The Pandas DataFrame to create nodes from.
            *args: Additional positional arguments.
            pd_kwargs (dict | None): Additional keyword arguments for Pandas DataFrame.
            **kwargs: Additional keyword arguments.

        Returns:
            list[T]: The list of created node instances.
        """
        if pd_kwargs is None:
            pd_kwargs = {}

        _objs = []
        for index, row in obj.iterrows():
            _obj = cls.from_obj(row, *args, **pd_kwargs, **kwargs)
            _obj.metadata["df_index"] = index
            _objs.append(_obj)

        return _objs

    @from_obj.register(BaseModel)
    @classmethod
    def _from_base_model(cls, obj, pydantic_kwargs=None, **kwargs) -> T:
        """
        Create a node instance from a Pydantic BaseModel.

        Args:
            obj (BaseModel): The Pydantic BaseModel to create the node from.

        Returns:
            T: The created node instance.
        """
        pydantic_kwargs = pydantic_kwargs or {"by_alias": True}
        try:
            config_ = {}
            try:
                config_ = obj.model_dump(**pydantic_kwargs)
            except:
                config_ = obj.to_dict(**pydantic_kwargs)
            else:
                config_ = obj.dict(**pydantic_kwargs)
        except Exception as e:
            raise ValueError(f"Invalid Pydantic model for deserialization: {e}") from e

        return cls.from_obj(config_ | kwargs)

    def meta_get(
        self, key: str, indices: list[str | int] | None = None, default: Any = None
    ) -> Any:
        """
        Get a value from the metadata dictionary.

        Args:
            key (str): The key to retrieve the value for.
            indices (list[str | int] | None): Optional list of indices for nested retrieval.
            default (Any): The default value to return if the key is not found.

        Returns:
            Any: The retrieved value or the default value if not found.
        """
        if indices:
            return nested.nget(self.metadata, indices, default)
        return self.metadata.get(key, default)

    def meta_change_key(self, old_key: str, new_key: str) -> bool:
        """
        Change a key in the metadata dictionary.

        Args:
            old_key (str): The old key to be changed.
            new_key (str): The new key to replace the old key.

        Returns:
            bool: True if the key was changed successfully, False otherwise.
        """
        if old_key in self.metadata:
            SysUtil.change_dict_key(self.metadata, old_key, new_key)
            return True
        return False

    def meta_insert(self, indices: str | list, value: Any, **kwargs) -> bool:
        """
        Insert a value into the metadata dictionary at the specified indices.

        Args:
            indices (str | list): The indices to insert the value at.
            value (Any): The value to be inserted.
            **kwargs: Additional keyword arguments for the `nested.ninsert`
                function.

        Returns:
            bool: True if the value was inserted successfully, False otherwise.
        """
        return nested.ninsert(self.metadata, indices, value, **kwargs)

    def meta_merge(
        self, additional_metadata: dict[str, Any], overwrite: bool = False, **kwargs
    ) -> None:
        """
        Merge additional metadata into the existing metadata dictionary.

        Args:
            additional_metadata (dict[str, Any]): The additional metadata to be
                merged.
            overwrite (bool): Whether to overwrite existing keys with the new
                values.
            **kwargs: Additional keyword arguments for the `nested.nmerge`
                function.
        """
        self.metadata = nested.nmerge(
            [self.metadata, additional_metadata], overwrite=overwrite, **kwargs
        )

    def to_llama_index(self, node_type: Type | str | Any = None, **kwargs) -> Any:
        """
        Serializes this node for LlamaIndex.

        Args:
            node_type (Type | str | Any): The type of node in LlamaIndex.
                Defaults to None.
            **kwargs: Additional keyword arguments for serialization.

        Returns:
            Any: The serialized node for LlamaIndex.
        """
        return LlamaIndexBridge.to_llama_index_node(self, node_type=node_type, **kwargs)

    def to_langchain(self, **kwargs) -> Any:
        """
        Serializes this node for Langchain.

        Args:
            **kwargs: Additional keyword arguments for serialization.

        Returns:
            Any: The serialized node for Langchain.
        """
        return LangchainBridge.to_langchain_document(self, **kwargs)


class Node(BaseNode):
    """
    Represents a node with relations to other nodes.

    Attributes:
        relations (Relations): The relations of the node, managed through a
            `Relations` instance.

    Properties:
        related_nodes: A set of IDs representing nodes related to this node.
        edges: A dictionary of all edges connected to this node.
        node_relations: A dictionary categorizing preceding and succeeding
            relations to this node.
        precedessors: A list of node IDs that precede this node.
        successors: A list of node IDs that succeed this node.

    Methods:
        relate(node, self_as, condition, **kwargs): Relates this node to
            another node with an edge.
        unrelate(node, edge): Removes one or all relations between this node
            and another.
        to_llama_index(node_type, **kwargs): Serializes this node for
            LlamaIndex.
        to_langchain(**kwargs): Serializes this node for Langchain.
        from_llama_index(llama_node, **kwargs): Deserializes a node from
            LlamaIndex data.
        from_langchain(lc_doc): Deserializes a node from Langchain data.
        __str__(): String representation of the node.

    Raises:
        ValueError: When invalid parameters are provided to methods.
    """

    relations: Relations = Field(
        default_factory=Relations,
        description="The relations of the node.",
        alias="node_relations",
    )

    mailbox: MailBox = Field(
        default_factory=MailBox,
        description="The mailbox for incoming and outgoing mails.",
    )

    @property
    def related_nodes(self) -> list[str]:
        """Returns a set of node IDs related to this node, excluding itself."""
        nodes = set(self.relations.all_nodes)
        nodes.discard(self.id_)
        return list(nodes)

    @property
    def edges(self) -> dict[str, Edge]:
        """Returns a dictionary of all edges connected to this node."""
        return self.relations.all_edges

    @property
    def node_relations(self) -> dict:
        """Categorizes preceding and succeeding relations to this node."""

        points_to_nodes = {}
        for edge in self.relations.points_to.values():
            for i in self.related_nodes:
                if edge.tail == i:
                    if i in points_to_nodes:
                        points_to_nodes[i].append(edge)
                    else:
                        points_to_nodes[i] = [edge]

        pointed_by_nodes = {}
        for edge in self.relations.pointed_by.values():
            for i in self.related_nodes:
                if edge.head == i:
                    if i in pointed_by_nodes:
                        pointed_by_nodes[i].append(edge)
                    else:
                        pointed_by_nodes[i] = [edge]

        return {"points_to": points_to_nodes, "pointed_by": pointed_by_nodes}

    @property
    def precedessors(self) -> list[str]:
        """return a list of nodes id that precede this node"""
        return [k for k, v in self.node_relations["pointed_by"].items() if len(v) > 0]

    @property
    def successors(self) -> list[str]:
        """return a list of nodes id that succeed this node"""
        return [k for k, v in self.node_relations["points_to"].items() if len(v) > 0]

    def relate(
        self,
        node: "Node",
        node_as: str = "head",
        condition: Condition | None = None,
        label: str | None = None,
        bundle=False,
    ) -> None:
        """Relates this node to another node with an edge.

        Args:
            node (Node): The node to relate to.
            self_as (str): Specifies whether this node is the 'head' or 'tail'
                of the relation. Defaults to "head".
            condition (Condition | None): The condition associated with the
                edge, if any. Defaults to None.
            **kwargs: Additional keyword arguments for edge creation.

        Raises:
            ValueError: If `self_as` is not 'head' or 'tail'.
        """
        if node_as == "head":
            edge = Edge(
                head=self, tail=node, condition=condition, bundle=bundle, label=label
            )
            self.relations.points_to[edge.id_] = edge
            node.relations.pointed_by[edge.id_] = edge

        elif node_as == "tail":
            edge = Edge(
                head=node, tail=self, condition=condition, label=label, bundle=bundle
            )
            self.relations.pointed_by[edge.id_] = edge
            node.relations.points_to[edge.id_] = edge

        else:
            raise ValueError(
                f"Invalid value for self_as: {node_as}, must be 'head' or 'tail'"
            )

    def remove_edge(self, node: "Node", edge: Edge | str) -> bool:
        if node.id_ not in self.related_nodes:
            raise ValueError(f"Node {self.id_} is not related to node {node.id_}.")

        edge_id = edge.id_ if isinstance(edge, Edge) else edge

        if (
            edge_id not in self.relations.all_edges
            or edge_id not in node.relations.all_edges
        ):
            raise ValueError(
                f"Edge {edge_id} does not exist between nodes {self.id_} and "
                f"{node.id_}."
            )

        all_dicts = [
            self.relations.points_to,
            self.relations.pointed_by,
            node.relations.points_to,
            node.relations.pointed_by,
        ]
        try:
            for _dict in all_dicts:
                edge_id = edge.id_ if isinstance(edge, Edge) else edge
                _dict.pop(edge_id, None)
            return True

        except Exception as e:
            raise ValueError(
                f"Failed to remove edge between nodes {self.id_} and " f"{node.id_}."
            ) from e

    def unrelate(self, node: "Node", edge: Edge | str = "all") -> bool:
        """
        Removes one or all relations between this node and another.

        Args:
            node (Node): The node to unrelate from.
            edge (Edge | str): Specific edge or 'all' to remove all relations.
                Defaults to "all".

        Returns:
            bool: True if the operation is successful, False otherwise.

        Raises:
            ValueError: If the node is not related or the edge does not exist.
        """
        if edge == "all":
            edge = self.node_relations["points_to"].get(
                node.id_, []
            ) + self.node_relations["pointed_by"].get(node.id_, [])
        else:
            edge = [edge.id_] if isinstance(edge, Edge) else [edge]

        if len(edge) == 0:
            raise ValueError(f"Node {self.id_} is not related to node {node.id_}.")

        try:
            for edge_id in edge:
                self.remove_edge(node, edge_id)
            return True
        except Exception as e:
            raise ValueError(
                f"Failed to remove edge between nodes {self.id_} and " f"{node.id_}."
            ) from e


    def __str__(self) -> str:
        """
        Provides a string representation of the node.

        Returns:
            str: The string representation of the node.
        """
        timestamp = f" ({self.timestamp})" if self.timestamp else ""
        if self.content:
            content_preview = (
                f"{self.content[:50]}..." if len(self.content) > 50 else self.content
            )
        else:
            content_preview = ""
        meta_preview = (
            f"{str(self.metadata)[:50]}..."
            if len(str(self.metadata)) > 50
            else str(self.metadata)
        )
        return (
            f"{self.class_name()}({self.id_}, {content_preview}, {meta_preview},"
            f"{timestamp})"
        )
