from typing import Tuple
from lion_core.generic.flow import Flow as CoreFlow
from lionagi.libs import lionfuncs as ln


class Flow(CoreFlow):

    @property
    def sequences(self):
        return self.progressions

    def all_unique_items(self) -> Tuple[str]:
        return self.unique()

    def to_df(self):
        return ln.to_df([prog.to_dict() for prog in self.progressions])


def flow(sequences=None, default_name=None, progressions=None):
    return Flow(
        progressions=progressions or sequences,
        default_name=default_name,
    )
