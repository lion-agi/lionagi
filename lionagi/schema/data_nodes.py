from .base_node import BaseNode



class DataNode(BaseNode):
    
    ...
    # def from_llama(self, data_:, **kwargs):
    #     ...
        
    # def to_llama(self, **kwargs):
    #     # to llama_index textnode
    #     ...
        
    # def from_langchain(self, data_, **kwargs):
    #     ...
    
    # def to_langchain(self, **kwargs):
    #     ...
        
    # def to_csv(self, **kwargs):
    #     ...

    # def __call__(self, file_=None):
    #     ...



class File(DataNode):
    ...
    
    # def from_path(self, path_, reader, clean=True, **kwargs):
    #     self.content = reader(path_=path_, clean=clean, **kwargs)
    
    # def to_chunks(self, chunker, **kwargs):
    #     ...


class Chunk(DataNode):
    ...    
    # @classmethod
    # def from_files(cls, files):
    #     ...    
    
    # @classmethod
    # def to_files(cls):
    #     ...


class Embeddings(DataNode):
    ...
