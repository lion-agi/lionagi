from lion_core.generic.log import BaseLog


class Log(BaseLog):
    pass


def log(content, loginfo):
    return Log(content=content, loginfo=loginfo)


__all__ = ["Log", "log"]
