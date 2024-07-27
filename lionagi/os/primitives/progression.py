from lion_core.generic.progression import Progression as CoreProgression


class Progression(CoreProgression):
    pass


def progression(*args, **kwargs):
    return Progression(*args, **kwargs)


__all__ = ["Progression", "progression"]
