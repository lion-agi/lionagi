# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import os
from enum import Enum

from jinja2 import Environment, FileSystemLoader, Template

base_dir = os.path.dirname(os.path.abspath(__file__))
templates_path = os.path.join(base_dir, "templates")
env = Environment(loader=FileSystemLoader(templates_path))

__all__ = (
    "BrainStormTemplate",
    "get_prompt",
)


class BrainStormTemplate(str, Enum):
    DEFAULT = "default.jinja2"
    COT = "chain_of_thoughts.jinja2"
    ONTOLOGICAL = "ontological.jinja2"


def get_prompt(template: BrainStormTemplate, **kwargs) -> str:
    template: Template = env.get_template(template.value)
    return template.render(**kwargs)
