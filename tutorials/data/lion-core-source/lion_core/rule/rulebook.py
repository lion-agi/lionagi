import inspect

from lionabc import BaseRecord
from lionabc.exceptions import LionTypeError, LionValueError
from lionfuncs import copy, to_dict
from pydantic import Field

from lion_core.generic.element import Element
from lion_core.generic.flow import Flow, flow
from lion_core.generic.note import Note, note
from lion_core.generic.pile import Pile, pile
from lion_core.rule.base import Rule
from lion_core.rule.default_rules._default import (
    DEFAULT_RULE_INFO,
    DEFAULT_RULEORDER,
)


class RuleBook(Element, BaseRecord):
    rules_info: Note = note()
    active_rules: Pile[Rule] = Field(
        default_factory=lambda: pile(
            item_type=Rule,
            strict_type=False,
        ),
        exclude=True,
    )
    default_rule_order: list = Field(default_factory=list)
    rule_flow: Flow = Field(default_factory=lambda: flow({}, "main"))

    def __init__(
        self,
        rules_info=DEFAULT_RULE_INFO,
        default_rule_order=DEFAULT_RULEORDER,
    ):
        super().__init__()
        self.rules_info = validate_rules_info(rules_info)
        self.default_rule_order = default_rule_order or list(
            self.rules_info.keys()
        )
        self.rule_flow.default_name = "main"

    def init_rule(
        self,
        rule: str | type[Rule],
        info: dict | Note = None,
        progress=None,
        **kwargs,
    ):
        if inspect.isclass(rule):
            rule = rule.__name__

        if isinstance(rule, str):
            rule = self.rules_info.get([rule, "rule"], None)

        if rule:
            _info = copy(self.rules_info[rule.__name__])
            _info.pop("rule")
            rule = rule(info=info or _info, **kwargs)
            rule._is_init = True
            self.active_rules.include(rule)
            self.rule_flow.append(rule, progress)
            return rule

        raise LionValueError(f"Invalid rule: {rule}")

    def get_rule_progress(self, progress):
        return self.rule_flow._find_prog(progress, None)


def validate_rules_info(rules_info):
    out = note()

    if isinstance(rules_info, Note):
        rules_info = to_dict(rules_info)["content"]

    if isinstance(rules_info, dict):
        for k, v in rules_info.items():
            v = to_dict(v)
            k: type[Rule] | None = k or v.get("rule", None)
            obj_ = rules_info[k]["rule"]
            if inspect.isclass(obj_) and not issubclass(obj_, Rule):

                raise LionTypeError(
                    message="Item type must be a subclass of Rule.",
                    expected_type=Rule,
                    actual_type=type(k),
                )

            v["rule"] = obj_
            out[k] = v

    return out


__all__ = ["RuleBook"]
