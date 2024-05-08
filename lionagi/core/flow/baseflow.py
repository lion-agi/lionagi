from abc import ABC


class BaseFlow(ABC):

    @classmethod
    def class_name(cls) -> str:
        """
        Returns the class name of the flow.
        """
        return cls.__name__


class BaseMonoFlow(BaseFlow):

    def __init__(self, branch, model=None) -> None:
        self.branch = branch
        self.model = model or branch.model


class BasePolyFlow(BaseFlow):

    def __init__(self, session, model=None) -> None:
        self.session = session
        self.model = model or session.model
