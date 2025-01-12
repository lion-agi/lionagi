# adapters/db_adapters.py
from typing import Any, Dict, List, TypeVar

from .base import Adapter

T = TypeVar("T")

# --- A. SQL Adapter using SQLAlchemy (simplified) ---
try:
    import sqlalchemy
    from sqlalchemy import (  # etc.
        Boolean,
        Column,
        Float,
        Integer,
        MetaData,
        String,
        Table,
        Text,
        select,
    )

    # optional: more refined column type mapping if you want
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False


class SQLAdapter(Adapter[T]):
    """
    An example adapter that reads/writes a single SQL table using SQLAlchemy.

    from_obj:
      - expects 'obj' to contain connection info (like a SQLAlchemy engine or a URI string)
      - also expects 'table_name' in kwargs
      - returns all rows from the table as list[dict]

    to_obj:
      - expects a list of dicts and writes them to the table (insert or replace).
      - you can specify 'if_exists' behavior, e.g. drop/create table, upsert, etc.
    """

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: Any, /, **kwargs) -> list[dict]:
        if not HAS_SQLALCHEMY:
            raise ImportError(
                "SQLAlchemy not installed, cannot use SQLAdapter."
            )

        table_name = kwargs.get("table_name")
        if not table_name:
            raise ValueError(
                "SQLAdapter.from_obj requires 'table_name' in kwargs."
            )

        # If obj is a connection URI, create engine
        if isinstance(obj, str):
            engine = sqlalchemy.create_engine(obj)
        elif isinstance(obj, sqlalchemy.engine.Engine):
            engine = obj
        else:
            raise ValueError(
                "SQLAdapter: 'obj' must be a SQLAlchemy engine or a connection string."
            )

        metadata = MetaData()
        metadata.reflect(bind=engine)
        if table_name not in metadata.tables:
            raise ValueError(f"Table '{table_name}' does not exist in DB.")

        table = metadata.tables[table_name]

        with engine.connect() as conn:
            stmt = select(table)
            result = conn.execute(stmt)
            rows = [dict(row) for row in result.fetchall()]

        return rows

    @classmethod
    def to_obj(cls, subj: list[dict], /, **kwargs) -> Any:
        """
        Insert or replace a list of dicts into the specified table.
        By default, it attempts a naive insert.
        If 'create_table=True' is provided, it tries to create the table
        based on the columns found in the first dict row (very simplistic).
        """
        if not HAS_SQLALCHEMY:
            raise ImportError(
                "SQLAlchemy not installed, cannot use SQLAdapter."
            )

        table_name = kwargs.get("table_name")
        if not table_name:
            raise ValueError(
                "SQLAdapter.to_obj requires 'table_name' in kwargs."
            )

        obj = kwargs.get("connection")  # can be a string or an engine
        if not obj:
            raise ValueError(
                "SQLAdapter.to_obj requires 'connection' in kwargs (engine or URI)."
            )

        create_table = kwargs.get("create_table", False)
        if isinstance(obj, str):
            engine = sqlalchemy.create_engine(obj)
        elif isinstance(obj, sqlalchemy.engine.Engine):
            engine = obj
        else:
            raise ValueError(
                "'connection' must be a SQLAlchemy engine or a URI string."
            )

        # Optional: create table if needed
        metadata = MetaData()
        if create_table and subj:
            # we just guess columns from the first row
            first_row = subj[0]
            columns = []
            for key, val in first_row.items():
                # naive type inference for demonstration
                if isinstance(val, int):
                    col_type = Integer()
                elif isinstance(val, float):
                    col_type = Float()
                elif isinstance(val, bool):
                    col_type = Boolean()
                else:
                    col_type = Text()

                columns.append(Column(key, col_type))

            table = Table(table_name, metadata, *columns)
            metadata.create_all(bind=engine, checkfirst=True)
        else:
            # reflect existing table
            metadata.reflect(bind=engine)
            if table_name not in metadata.tables:
                raise ValueError(
                    f"Table '{table_name}' not found, and create_table=False."
                )
            table = metadata.tables[table_name]

        # Now do inserts
        with engine.connect() as conn:
            if subj:
                conn.execute(table.insert(), subj)

        return f"{len(subj)} records inserted into {table_name}"


# --- B. MongoDB Adapter using PyMongo (simplified) ---
try:
    import pymongo  # type: ignore

    HAS_PYMONGO = True
except ImportError:
    HAS_PYMONGO = False


class MongoAdapter(Adapter[T]):
    """
    A simple adapter for MongoDB using PyMongo.
    from_obj:
      - expects a dict with { 'uri': <mongo URI>, 'db_name': <>, 'collection_name': <> }
      - returns all docs from that collection as list[dict]
    to_obj:
      - insert or replace docs into that collection
    """

    @classmethod
    def from_obj(cls, subj_cls: type[T], obj: Any, /, **kwargs) -> list[dict]:
        if not HAS_PYMONGO:
            raise ImportError(
                "PyMongo not installed, cannot use MongoAdapter."
            )

        if not isinstance(obj, dict):
            raise ValueError(
                "MongoAdapter: 'obj' must be a dict with 'uri', 'db_name', 'collection_name'."
            )

        uri = obj.get("uri")
        db_name = obj.get("db_name")
        coll_name = obj.get("collection_name")
        if not uri or not db_name or not coll_name:
            raise ValueError(
                "MongoAdapter requires 'uri', 'db_name', and 'collection_name' in obj dict."
            )

        client = pymongo.MongoClient(uri)
        coll = client[db_name][coll_name]

        # Query (you can pass filter in kwargs or do a full collection find)
        query_filter = kwargs.get("filter", {})
        cursor = coll.find(query_filter)
        data = [doc for doc in cursor]
        # Remove _id if you prefer not to keep it
        for d in data:
            d.pop("_id", None)
        return data

    @classmethod
    def to_obj(cls, subj: list[dict], /, **kwargs) -> Any:
        if not HAS_PYMONGO:
            raise ImportError(
                "PyMongo not installed, cannot use MongoAdapter."
            )

        obj = kwargs.get("connection")
        if not obj or not isinstance(obj, dict):
            raise ValueError(
                "MongoAdapter.to_obj requires 'connection' dict with 'uri', 'db_name', 'collection_name'."
            )

        uri = obj.get("uri")
        db_name = obj.get("db_name")
        coll_name = obj.get("collection_name")
        if not uri or not db_name or not coll_name:
            raise ValueError(
                "MongoAdapter connection requires 'uri', 'db_name', and 'collection_name'"
            )

        client = pymongo.MongoClient(uri)
        coll = client[db_name][coll_name]

        # naive insertMany
        if subj:
            insert_result = coll.insert_many(subj)
            return f"Inserted {len(insert_result.inserted_ids)} documents."
        else:
            return "No documents to insert."
