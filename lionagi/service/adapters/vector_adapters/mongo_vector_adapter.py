# adapters/vector/mongo_vector_adapter.py
"""MongoDB Vector Adapter implementation.

Provides a comprehensive interface for vector similarity search and storage:
- Vector similarity search using $vectorSearch
- Batch operations for vectors and metadata
- Connection pooling and management
- Automatic index creation and maintenance
- Comprehensive error handling
"""

from typing import Any, Dict, List, Optional, TypeVar, Union, Iterator
from dataclasses import dataclass
from contextlib import contextmanager
import logging
from datetime import datetime

from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import (
    ConnectionFailure, 
    OperationFailure, 
    BulkWriteError,
    InvalidOperation
)

from ..base import Adapter
from ....._errors import LionError

T = TypeVar("T")

# Configure logging
logger = logging.getLogger(__name__)

class MongoVectorError(LionError):
    """Base exception for MongoDB Vector operations."""
    pass

class MongoConnectionError(MongoVectorError):
    """Raised when connection to MongoDB fails."""
    pass

class MongoQueryError(MongoVectorError):
    """Raised when query execution fails."""
    pass

class MongoIndexError(MongoVectorError):
    """Raised when index operations fail."""
    pass

class MongoDataError(MongoVectorError):
    """Raised when data validation fails."""
    pass

@dataclass
class MongoConfig:
    """MongoDB connection and collection configuration."""
    connection_string: str
    db_name: str
    collection_name: str
    vector_dim: int
    index_name: str = "vector_index"
    pool_size: int = 100
    timeout_ms: int = 5000

class MongoConnectionManager:
    """Manages MongoDB connections and index creation."""
    
    def __init__(self, config: MongoConfig):
        self.config = config
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
        self._collection: Optional[Collection] = None

    @contextmanager
    def connect(self):
        """Context manager for MongoDB connections."""
        try:
            if not self._client:
                self._client = MongoClient(
                    self.config.connection_string,
                    maxPoolSize=self.config.pool_size,
                    serverSelectionTimeoutMS=self.config.timeout_ms
                )
                self._db = self._client[self.config.db_name]
                self._collection = self._db[self.config.collection_name]
                self._ensure_indexes()
            
            yield self._collection
        
        except ConnectionFailure as e:
            raise MongoConnectionError(f"Failed to connect: {str(e)}")
        except Exception as e:
            raise MongoVectorError(f"Unexpected error: {str(e)}")
        
    def _ensure_indexes(self):
        """Create required indexes if they don't exist."""
        try:
            # Create vector search index
            index_model = {
                "mappings": {
                    "dynamic": True,
                    "fields": {
                        "vector": {
                            "dimensions": self.config.vector_dim,
                            "similarity": "cosine",
                            "type": "knnVector"
                        }
                    }
                }
            }
            
            self._collection.create_search_index(
                self.config.index_name,
                index_model,
                exist_ok=True
            )
            
            # Create standard indexes
            self._collection.create_index([("metadata.timestamp", ASCENDING)])
            self._collection.create_index([("metadata.type", ASCENDING)])
            
        except OperationFailure as e:
            raise MongoIndexError(f"Failed to create indexes: {str(e)}")

class MongoVectorAdapter(Adapter[T]):
    """
    MongoDB Vector Adapter supporting vector similarity search and storage.
    
    Features:
    - Vector similarity search using $vectorSearch
    - Metadata filtering
    - Batch operations
    - Connection pooling
    - Automatic index creation
    - Comprehensive error handling
    
    Usage:
        config = MongoConfig(
            connection_string="mongodb://...",
            db_name="vector_db",
            collection_name="embeddings",
            vector_dim=1536
        )
        
        adapter = MongoVectorAdapter(config)
        
        # Search similar vectors
        results = adapter.from_obj(
            Vector,
            {
                "vector": [0.1, 0.2, ...],
                "filter": {"metadata.type": "document"},
                "limit": 10
            }
        )
        
        # Store vectors
        adapter.to_obj(
            [
                {
                    "id": "doc1",
                    "vector": [0.1, 0.2, ...],
                    "metadata": {"type": "document"}
                }
            ]
        )
    """
    
    def __init__(self, config: MongoConfig):
        self.conn_manager = MongoConnectionManager(config)

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: Dict[str, Any], /, **kwargs) -> List[Dict]:
        """
        Perform vector similarity search with optional metadata filtering.
        
        Args:
            obj: Dict containing:
                - vector: List[float] - Query vector
                - filter: Optional[Dict] - Metadata filters
                - limit: Optional[int] - Max results (default 10)
                - min_score: Optional[float] - Minimum similarity score
            
        Returns:
            List[Dict] containing matched documents with scores
            
        Raises:
            MongoQueryError: If search operation fails
            MongoDataError: If input validation fails
        """
        try:
            if not isinstance(obj, dict):
                raise MongoDataError("Input must be a dictionary")
                
            vector = obj.get("vector")
            if not vector or not isinstance(vector, list):
                raise MongoDataError("Valid vector required")
                
            filter_dict = obj.get("filter", {})
            limit = obj.get("limit", 10)
            min_score = obj.get("min_score", 0.0)
            
            pipeline = [
                {
                    "$vectorSearch": {
                        "queryVector": vector,
                        "path": "vector",
                        "numCandidates": limit * 10,
                        "limit": limit,
                        "minScore": min_score,
                        "filter": filter_dict
                    }
                },
                {
                    "$project": {
                        "id": "$_id",
                        "vector": 1,
                        "metadata": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]
            
            with cls.conn_manager.connect() as collection:
                results = list(collection.aggregate(pipeline))
                return results
                
        except OperationFailure as e:
            raise MongoQueryError(f"Search failed: {str(e)}")
        except Exception as e:
            raise MongoVectorError(f"Unexpected error: {str(e)}")

    @classmethod
    def to_obj(cls, subj: List[Dict], /, **kwargs) -> str:
        """
        Store or update vectors and metadata using bulk operations.
        
        Args:
            subj: List[Dict] containing documents with:
                - id: str
                - vector: List[float]
                - metadata: Optional[Dict]
            
        Returns:
            str: Operation summary
            
        Raises:
            MongoDataError: If document validation fails
            MongoQueryError: If bulk write fails
        """
        try:
            if not isinstance(subj, list):
                raise MongoDataError("Input must be a list of documents")
                
            ops = []
            for doc in subj:
                if "id" not in doc or "vector" not in doc:
                    raise MongoDataError("Documents must have 'id' and 'vector' fields")
                    
                doc_id = doc.pop("id")
                doc["_id"] = doc_id
                doc["metadata"] = doc.get("metadata", {})
                doc["metadata"]["timestamp"] = datetime.utcnow()
                
                ops.append(
                    {
                        "replaceOne": {
                            "filter": {"_id": doc_id},
                            "replacement": doc,
                            "upsert": True
                        }
                    }
                )
            
            if not ops:
                return "No documents to write"
                
            with cls.conn_manager.connect() as collection:
                result = collection.bulk_write(ops, ordered=False)
                return (
                    f"Processed {len(ops)} documents: "
                    f"inserted {result.upserted_count}, "
                    f"modified {result.modified_count}"
                )
                
        except BulkWriteError as e:
            raise MongoQueryError(f"Bulk write failed: {str(e)}")
        except Exception as e:
            raise MongoVectorError(f"Unexpected error: {str(e)}")
