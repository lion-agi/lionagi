from enum import Enum
from pathlib import Path
from typing import ClassVar, Literal

from pydantic import Field, PrivateAttr

from lionagi.protocols._concepts import Manager
from lionagi.protocols.generic.pile import Pile
from lionagi.protocols.graph.graph import Graph
from lionagi.protocols.graph.node import Node

from ..base import MetaModel, Resource, ResourceCategory


class DocRelations(str, Enum):

    CHUNK_OF = "chunk_of"  # chunk is part of a document
    NEXT_CHUNK_OF = "next_chunk_of"  # chunk is next in sequence
    REFERENCE_OF = "reference_of"  # quotes, citations, etc.
    TRANSFORMATION_OF = "transformation_of"  # symbolic transformations...


class DocumentMeta(MetaModel):

    name: str | None = None
    fp: str | Path | None = None
    url: str | None = None
    from_url: bool | None = None
    extension: str | None = None
    size: int | None = None
    original_created_at: str | None = None
    last_modified_at: str | None = None
    mime_type: str | None = None
    encoding: str | None = None
    chunk_name: str | None = None
    chunk_order: int | None = None
    chunk_start: int | None = None
    chunk_end: int | None = None


class Document(Resource):

    meta_type: ClassVar[type[MetaModel]] = DocumentMeta
    category: ResourceCategory = Field(
        default=ResourceCategory.DOCUMENT, frozen=True
    )


DOCUMENT_PROVIDER_CAPABILITIES = Literal["read", "transform", "chunk"]
