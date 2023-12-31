import json
from typing import Union, Callable

from ..schema.base_schema import DataNode


def from_langchain(lc_doc):
    info_json = lc_doc.to_json()
    info_node = {'lc_id': info_json['id']}
    info_node = {**info_node, **info_json['kwargs']}
    return DataNode(**info_node)


def to_langchain_document(datanode, **kwargs):
    # to langchain document
    from langchain.schema import Document

    dnode = json.loads(datanode.to_json())
    dnode['page_content'] = dnode.pop('content')
    dnode = {**dnode, **kwargs}
    return Document(**dnode)


def langchain_loader(loader: Union[str, Callable], loader_args=[], loader_kwargs={}):
    import langchain.document_loaders as document_loaders

    try:
        if isinstance(loader, str):
            loader_ = getattr(document_loaders, loader)
        else:
            loader_ = loader
    except Exception as e:
        raise ValueError(f'Invalid loader: {loader}. Error: {e}')

    try:
        loader_obj = loader_(*loader_args, **loader_kwargs)
        data = loader_obj.load()
        return data
    except Exception as e:
        raise ValueError(f'Failed to load. Error: {e}')


def langchain_text_splitter(data, splitter: Union[str, Callable], splitter_args=[], splitter_kwargs={}):
    import langchain.text_splitter as text_splitter

    try:
        if isinstance(splitter, str):
            splitter_ = getattr(text_splitter, splitter)
        else:
            splitter_ = splitter
    except Exception as e:
        raise ValueError(f'Invalid text splitter: {text_splitter}. Error: {e}')

    try:
        splitter_obj = splitter_(*splitter_args, **splitter_kwargs)
        chunk = splitter_obj.split_text(data)
        return chunk
    except Exception as e:
        raise ValueError(f'Failed to split. Error: {e}')


def langchain_code_splitter(doc: str, language: str, splitter_args=[], splitter_kwargs={}):
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    try:
        splitter = RecursiveCharacterTextSplitter.from_language(language=language, *splitter_args, **splitter_kwargs)
        docs = splitter.create_documents([doc])
        return docs
    except Exception as e:
        raise ValueError(f'Failed to split. Error: {e}')