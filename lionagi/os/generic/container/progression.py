from lion_core.generic.progression import Progression as CoreProgression


class Progression(CoreProgression):
    pass


def prog(*args, **kwargs):
    return Progression(*args, **kwargs)


def progression(*args, **kwargs):  # for backward compatibility
    return prog(*args, **kwargs)


__all__ = ["Progression", "prog", "progression"]
