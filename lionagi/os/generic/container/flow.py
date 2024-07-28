from lion_core.generic.flow import Flow as CoreFlow


class Flow(CoreFlow):
    pass


def flow(*args, **Kwargs):
    return Flow(*args, **Kwargs)


__all__ = ["Flow", "flow"]
