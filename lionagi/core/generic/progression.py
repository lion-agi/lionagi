from lion_core.generic.progression import Progression as CoreProgression


class Progression(CoreProgression):

    def keys(self):
        yield from range(len(self))

    def values(self):
        yield from self.order

    def items(self):
        for idx, item in enumerate(self.order):
            yield idx, item

    def copy(self):
        """create a deep copy"""
        return self.model_copy()

    def __eq__(self, other):
        """Compare two Progression instances for equality."""
        if not isinstance(other, Progression):
            return NotImplemented
        return self.order == other.order and self.name == other.name


def progression(order=None, name=None) -> Progression:
    return Progression(order=order, name=name)
