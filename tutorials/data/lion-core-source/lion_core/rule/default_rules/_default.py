from lion_core.generic.note import note
from lion_core.rule.default_rules.boolean import BooleanRule
from lion_core.rule.default_rules.choice import ChoiceRule
from lion_core.rule.default_rules.function_calling import FunctionCallingRule
from lion_core.rule.default_rules.mapping import MappingRule
from lion_core.rule.default_rules.number import NumberRule
from lion_core.rule.default_rules.string import StringRule

base_boolean_config = {"apply_types": ["bool"], "rule": BooleanRule}

base_choice_config = {
    "apply_types": ["enum"],
    "accept_info_key": {"keys"},
    "rule": ChoiceRule,
}

base_mapping_config = {
    "apply_types": ["dict"],
    "accept_info_key": {"keys"},
    "score_func": None,
    "fuzzy_match": True,
    "fill_value": None,
    "fill_mapping": None,
    "strict": False,
    "handle_unmatched": "force",
    "rule": MappingRule,
}

base_function_calling_config = {
    "apply_types": ["functioncalling"],
    "accept_info_key": {"keys", "discard"},
    "keys": ["function", "arguments"],
    "discard": True,
    "rule": FunctionCallingRule,
}

base_number_config = {
    "apply_types": ["int", "float", "complex"],
    "upper_bound": None,
    "lower_bound": None,
    "num_type": "float",
    "precision": None,
    "num_count": 1,
    "rule": NumberRule,
}

base_string_config = {
    "use_model_dump": True,
    "strip_lower": False,
    "chars": None,
    "apply_types": ["str"],
    "rule": StringRule,
}

DEFAULT_RULE_INFO = note(
    **{
        "ChoiceRule": base_choice_config,
        "MappingRule": base_mapping_config,
        "FunctionCallingRule": base_function_calling_config,
        "NumberRule": base_number_config,
        "BooleanRule": base_boolean_config,
        "StringRule": base_string_config,
    }
)

DEFAULT_RULEORDER = [
    "ChoiceRule",
    "MappingRule",
    "FunctionCallingRule",
    "NumberRule",
    "BooleanRule",
    "StringRule",
]
