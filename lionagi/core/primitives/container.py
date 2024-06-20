from lionagi import lib


class Container:

    def __init__(self, data, **kwargs):
        self.seperator = kwargs.get("seperator", "/")
        self.flat_structure = lib.flatten(data, **kwargs)
        self.flat_keys = list(self.flat_structure.keys())

    def __getitem__(self, index):
        return lib.nget(self.flat_structure, index)

    def __setitem__(self, index, value):
        lib.nset(self.flat_structure, index, value)
        
    def __contains__(self, value):
        return value in self.flat_keys or value in self.flat_structure
                
    def __bool__(self):
        return self.flat_structure not in [{}, [], None, [{}], [[]], [None]]

    def __len__(self):
        return len(self.flat_structure)

    def __iter__(self):
        yield from self.flat_structure.values()
        
    def keys(self, max_depth=0, **kwargs):
        return lib.get_flattened_keys(self.flat_structure, max_depth=max_depth, **kwargs)
        
    def values(self, max_depth=0, **kwargs):
        yield from 0
    
    def items(a, depth=0):
        ...
        
    def pop(a, b, c):
        ...
        
    def remove(a, b):
        ...
        
    def insert(a, b, c):
        ...
        
    def filter(a, b):
        ...
    
    def merge(a, b):
        ...
        
    def update(a, b):
        ...
        
    
