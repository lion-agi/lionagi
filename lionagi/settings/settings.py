# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from datetime import UTC, timezone

__all__ = ("Settings",)


class SettingsClass:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    class Config:
        ENV_FILE: str = ".env"
        TIMEZONE: timezone = UTC


Settings = SettingsClass()
