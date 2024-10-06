from collections.abc import Sequence
from pathlib import Path

from lionabc import Observable
from lion_core.setting import DEFAULT_LION_ID_CONFIG, LionIDConfig
from lion_core.sys_utils import SysUtil as _u


PATH_TYPE = str | Path


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
        return _u.id(
            config=config,
            n=n,
            prefix=prefix,
            postfix=postfix,
            random_hyphen=random_hyphen,
            num_hyphens=num_hyphens,
            hyphen_start_index=hyphen_start_index,
            hyphen_end_index=hyphen_end_index,
        )

    @staticmethod
    def get_id(
        item: Sequence[Observable] | Observable | str,
        config: LionIDConfig = DEFAULT_LION_ID_CONFIG,
        /,
    ) -> str:
        return _u.get_id(item, config)

    @staticmethod
    def is_id(
        item: Sequence[Observable] | Observable | str,
        config: LionIDConfig = DEFAULT_LION_ID_CONFIG,
        /,
    ) -> bool:
        return _u.is_id(item, config)
