from lion_core.generic.flow import Flow


def flow(progressions=None, default_name=None):
    return Flow(
        progressions,
        default_name,
    )


__all__ = ["Flow", "flow"]
