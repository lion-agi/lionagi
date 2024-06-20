from lionagi.os.lib.sys_util import get_timestamp
from lionagi.os.lib import nget, nset, ninsert, flatten, unflatten
from typing import TypeVar

T = TypeVar("T")


class ComponentMetaManageMixin:

    def _add_last_update(self, name):
        if (a := nget(self.metadata, ["last_updated", name], None)) is None:
            ninsert(
                self.metadata,
                ["last_updated", name],
                get_timestamp(sep=None)[:-6],
            )
        elif isinstance(a, tuple) and isinstance(a[0], int):
            nset(
                self.metadata,
                ["last_updated", name],
                get_timestamp(sep=None)[:-6],
            )

    def _meta_pop(self, indices, default=...):
        indices = (
            indices
            if not isinstance(indices, list)
            else "|".join([str(i) for i in indices])
        )
        dict_ = self.metadata.copy()
        dict_ = flatten(dict_)

        try:
            out_ = dict_.pop(indices, default) if default != ... else dict_.pop(indices)
        except KeyError as e:
            if default == ...:
                raise KeyError(f"Key {indices} not found in metadata.") from e
            return default

        a = unflatten(dict_)
        self.metadata.clear()
        self.metadata.update(a)
        return out_

    def _meta_insert(self, indices, value):
        ninsert(self.metadata, indices, value)

    def _meta_set(self, indices, value):
        if not self._meta_get(indices):
            self._meta_insert(indices, value)
        nset(self.metadata, indices, value)

    def _meta_get(self, indices, default=...):
        if default != ...:
            return nget(self.metadata, indices=indices, default=default)
        return nget(self.metadata, indices)
