from lion_core.generic.note import Note as CoreNote


class Note(CoreNote):
    pass


def note(*args, **kwargs):
    return Note(*args, **kwargs)


__all__ = ["Note"]
