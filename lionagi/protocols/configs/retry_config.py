# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0


from lionagi.core.models.schema_model import SchemaModel
from lionagi.libs.constants import UNDEFINED, UndefinedType


class TimedFuncCallConfig(SchemaModel):
    initial_delay: int = 0
    retry_default: str | UndefinedType = UNDEFINED
    retry_timeout: int | None = None
    retry_timing: bool = False
    error_msg: str | None = None
    error_map: dict | None = None


class RetryConfig(SchemaModel):
    num_retries: int = 0
    initial_delay: int = 0
    retry_delay: int = 0
    backoff_factor: int = 1
    retry_default: str | UndefinedType = UNDEFINED
    retry_timeout: int | None = None
    retry_timing: bool = False
    verbose_retry: bool = False
    error_msg: str | None = None
    error_map: dict | None = None
