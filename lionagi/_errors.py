class LionError(Exception):
    pass


class ItemNotFoundError(LionError):
    pass


class ItemExistsError(LionError):
    pass


class IDError(LionError):
    pass


class RelationError(LionError):
    pass
