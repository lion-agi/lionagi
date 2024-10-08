import os
from collections.abc import Sequence
from hashlib import sha256
from typing import TypeVar

from lionabc import Observable
from lionabc.exceptions import LionIDError
from lionfuncs import insert_random_hyphens, time

from lion_core.setting import DEFAULT_LION_ID_CONFIG, LionIDConfig

T = TypeVar("T")


class SysUtil:

    @staticmethod
    def id(
        config: LionIDConfig = DEFAULT_LION_ID_CONFIG,
        n: int = None,
        prefix: str = None,
        postfix: str = None,
        random_hyphen: bool = None,
        num_hyphens: int = None,
        hyphen_start_index: int = None,
        hyphen_end_index: int = None,
    ) -> str:
        _dict = {
            "n": n,
            "prefix": prefix,
            "postfix": postfix,
            "random_hyphen": random_hyphen,
            "num_hyphens": num_hyphens,
            "hyphen_start_index": hyphen_start_index,
            "hyphen_end_index": hyphen_end_index,
        }
        _dict = {k: v for k, v in _dict.items() if v is not None}
        config = {**config.to_dict(), **_dict}
        return SysUtil._id(**config)

    @staticmethod
    def _id(
        *,
        n: int,
        prefix: str = "",
        postfix: str = "",
        random_hyphen: bool = False,
        num_hyphens: int = 0,
        hyphen_start_index: int = 6,
        hyphen_end_index: int = -6,
    ) -> str:
        """
        Generate a unique identifier.

        Args:
            n: Length of the ID (excluding prefix and postfix).
            prefix: String to prepend to the ID.
            postfix: String to append to the ID.
            random_hyphen: If True, insert random hyphens into the ID.
            num_hyphens: Number of hyphens to insert if random_hyphen is True.
            hyphen_start_index: Start index for hyphen insertion.
            hyphen_end_index: End index for hyphen insertion.

        Returns:
            A unique identifier string.
        """
        _t = time(type_="iso").encode()
        _r = os.urandom(16)
        _id = sha256(_t + _r).hexdigest()[:n]

        if random_hyphen:
            _id = insert_random_hyphens(
                s=_id,
                num_hyphens=num_hyphens,
                start_index=hyphen_start_index,
                end_index=hyphen_end_index,
            )

        if prefix:
            _id = f"{prefix}{_id}"
        if postfix:
            _id = f"{_id}{postfix}"

        return _id

    @staticmethod
    def get_id(
        item: Sequence[Observable] | Observable | str,
        config: LionIDConfig = DEFAULT_LION_ID_CONFIG,
        /,
    ) -> str:
        """
        Get the Lion ID of an item.

        Args:
            item: The item to get the ID from.
            config: Configuration dictionary for ID validation.

        Returns:
            The Lion ID of the item.

        Raises:
            LionIDError: If the item does not contain a valid Lion ID.
        """

        item_id = None
        if isinstance(item, Sequence) and len(item) == 1:
            item = item[0]

        if isinstance(item, Observable):
            item_id: str = item.ln_id
        else:
            item_id = item

        check = isinstance(item_id, str)
        if check:
            id_len = (
                (len(config.prefix) if config.prefix else 0)
                + config.n
                + config.num_hyphens
                + (len(config.postfix) if config.postfix else 0)
            )
            if len(item_id) != id_len:
                check = False
        if check and config.prefix:
            if item_id.startswith(config.prefix):
                item_id = item_id[len(config.prefix) :]  # noqa
            else:
                check = False
        if check and config.postfix:
            if item_id.endswith(config.postfix):
                item_id = item_id[: -len(config.postfix)]
            else:
                check = False
        if check and config.num_hyphens:
            if config.num_hyphens != item_id.count("-"):
                check = False
        if check and config.hyphen_start_index:
            idx = config.hyphen_start_index - len(config.prefix)
            if idx > 0 and "-" in item_id[:idx]:
                check = False
        if check and config.hyphen_end_index:
            if config.hyphen_end_index < 0:
                idx = config.hyphen_end_index + id_len
            idx -= len(config.prefix + config.postfix)
            if idx < 0 and "-" in item_id[idx:]:
                check = False

        if check:
            return config.prefix + item_id + config.postfix
        if (
            isinstance(item_id, str) and len(item_id) == 32
        ):  # for backward compatibility
            return item_id
        raise LionIDError(
            f"The input object of type <{type(item).__name__}> does "
            "not contain or is not a valid Lion ID. Item must be an instance"
            " of `Observable` or a valid `ln_id`."
        )

    @staticmethod
    def is_id(
        item: Sequence[Observable] | Observable | str,
        config: LionIDConfig = DEFAULT_LION_ID_CONFIG,
        /,
    ) -> bool:
        """
        Check if an item is a valid Lion ID.

        Args:
            item: The item to check.
            config: Configuration dictionary for ID validation.

        Returns:
            True if the item is a valid Lion ID, False otherwise.
        """
        try:
            SysUtil.get_id(item, config)
            return True
        except LionIDError:
            return False
