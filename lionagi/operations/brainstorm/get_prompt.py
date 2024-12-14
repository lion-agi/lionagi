import os
from enum import Enum

from jinja2 import Environment, FileSystemLoader, Template

base_dir = os.path.dirname(os.path.abspath(__file__))
templates_path = os.path.join(base_dir, "templates")
env = Environment(loader=FileSystemLoader(templates_path))

__all__ = (
    "BrainStormTemplate",
    "match_template",
)


class BrainStormTemplate(str, Enum):
    DEFAULT = "default.jinja2"
    COT = "chain_of_thoughts.jinja2"
    ONTOLOGICAL = "ontological.jinja2"


def match_template(template: BrainStormTemplate, **kwargs) -> str:
    template: Template = env.get_template(template.value)
    return template.render(**kwargs)
