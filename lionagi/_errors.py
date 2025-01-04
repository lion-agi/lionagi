# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0


class LionError(Exception):
    pass


class ItemNotFoundError(LionError):
    pass


class ItemExistsError(LionError):
    pass


class IDError(LionError):
    pass


class RelationError(LionError):
    pass


class RateLimitError(LionError):
    pass


class OperationError(LionError):
    pass


class ExecutionError(LionError):
    pass
