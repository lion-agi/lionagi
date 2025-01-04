# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Literal

from ..nested.flatten import flatten


def extract_json_schema(
    data: Any,
    *,
    sep: str = "|",
    coerce_keys: bool = True,
    dynamic: bool = True,
    coerce_sequence: Literal["dict", "list"] | None = None,
    max_depth: int | None = None,
) -> dict[str, Any]:
    """
    Extract a JSON schema from JSON data.

    This function uses the flatten function to create a flat representation
    of the JSON data, then builds a schema based on the flattened structure.

    Args:
        data: The JSON data to extract the schema from.
        sep: Separator used in flattened keys.
        coerce_keys: Whether to coerce keys to strings.
        dynamic: Whether to use dynamic flattening.
        coerce_sequence: How to coerce sequences ("dict", "list", or None).
        max_depth: Maximum depth to flatten.

    Returns:
        A dictionary representing the JSON schema.
    """
    flattened = flatten(
        data,
        sep=sep,
        coerce_keys=coerce_keys,
        dynamic=dynamic,
        coerce_sequence=coerce_sequence,
        max_depth=max_depth,
    )

    schema = {}
    for key, value in flattened.items():
        key_parts = key.split(sep) if isinstance(key, str) else key
        current = schema
        for part in key_parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        current[key_parts[-1]] = _get_type(value)

    return {"type": "object", "properties": _consolidate_schema(schema)}


def _get_type(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        return {"type": "string"}
    elif isinstance(value, bool):
        return {"type": "boolean"}
    elif isinstance(value, int):
        return {"type": "integer"}
    elif isinstance(value, float):
        return {"type": "number"}
    elif isinstance(value, list):
        if not value:
            return {"type": "array", "items": {}}
        item_types = [_get_type(item) for item in value]
        if all(item_type == item_types[0] for item_type in item_types):
            return {"type": "array", "items": item_types[0]}
        else:
            return {"type": "array", "items": {"oneOf": item_types}}
    elif isinstance(value, dict):
        return {
            "type": "object",
            "properties": _consolidate_schema(
                {k: _get_type(v) for k, v in value.items()}
            ),
        }
    elif value is None:
        return {"type": "null"}
    else:
        return {"type": "any"}


def _consolidate_schema(schema: dict) -> dict:
    """
    Consolidate the schema to handle lists and nested structures.
    """
    consolidated = {}
    for key, value in schema.items():
        if isinstance(value, dict) and all(k.isdigit() for k in value.keys()):
            # This is likely a list
            item_types = list(value.values())
            if all(item_type == item_types[0] for item_type in item_types):
                consolidated[key] = {"type": "array", "items": item_types[0]}
            else:
                consolidated[key] = {
                    "type": "array",
                    "items": {"oneOf": item_types},
                }
        elif isinstance(value, dict) and "type" in value:
            consolidated[key] = value
        else:
            consolidated[key] = _consolidate_schema(value)
    return consolidated


def json_schema_to_cfg(
    schema: dict[str, Any], start_symbol: str = "S"
) -> list[tuple[str, list[str]]]:
    productions = []
    visited = set()
    symbol_counter = 0

    def generate_symbol(base: str) -> str:
        nonlocal symbol_counter
        symbol = f"{base}@{symbol_counter}"
        symbol_counter += 1
        return symbol

    def generate_rules(s: dict[str, Any], symbol: str):
        if symbol in visited:
            return
        visited.add(symbol)

        if s.get("type") == "object":
            properties = s.get("properties", {})
            if properties:
                props_symbol = generate_symbol("PROPS")
                productions.append((symbol, ["{", props_symbol, "}"]))

                productions.append((props_symbol, []))  # Empty object
                for i, prop in enumerate(properties):
                    prop_symbol = generate_symbol(prop)
                    if i == 0:
                        productions.append((props_symbol, [prop_symbol]))
                    else:
                        productions.append(
                            (props_symbol, [props_symbol, ",", prop_symbol])
                        )

                for prop, prop_schema in properties.items():
                    prop_symbol = generate_symbol(prop)
                    value_symbol = generate_symbol("VALUE")
                    productions.append(
                        (prop_symbol, [f'"{prop}"', ":", value_symbol])
                    )
                    generate_rules(prop_schema, value_symbol)
            else:
                productions.append((symbol, ["{", "}"]))

        elif s.get("type") == "array":
            items = s.get("items", {})
            items_symbol = generate_symbol("ITEMS")
            value_symbol = generate_symbol("VALUE")
            productions.append((symbol, ["[", "]"]))
            productions.append((symbol, ["[", items_symbol, "]"]))
            productions.append((items_symbol, [value_symbol]))
            productions.append(
                (items_symbol, [value_symbol, ",", items_symbol])
            )
            generate_rules(items, value_symbol)

        elif s.get("type") == "string":
            productions.append((symbol, ["STRING"]))

        elif s.get("type") == "number":
            productions.append((symbol, ["NUMBER"]))

        elif s.get("type") == "integer":
            productions.append((symbol, ["INTEGER"]))

        elif s.get("type") == "boolean":
            productions.append((symbol, ["BOOLEAN"]))

        elif s.get("type") == "null":
            productions.append((symbol, ["NULL"]))

    generate_rules(schema, start_symbol)
    return productions


def json_schema_to_regex(schema: dict[str, Any]) -> str:
    def schema_to_regex(s):
        if s.get("type") == "object":
            properties = s.get("properties", {})
            prop_patterns = [
                rf'"{prop}"\s*:\s*{schema_to_regex(prop_schema)}'
                for prop, prop_schema in properties.items()
            ]
            return (
                r"\{"
                + r"\s*("
                + r"|".join(prop_patterns)
                + r")"
                + r"(\s*,\s*("
                + r"|".join(prop_patterns)
                + r"))*\s*\}"
            )
        elif s.get("type") == "array":
            items = s.get("items", {})
            return (
                r"\[\s*("
                + schema_to_regex(items)
                + r"(\s*,\s*"
                + schema_to_regex(items)
                + r")*)?\s*\]"
            )
        elif s.get("type") == "string":
            return r'"[^"]*"'
        elif s.get("type") == "integer":
            return r"-?\d+"
        elif s.get("type") == "number":
            return r"-?\d+(\.\d+)?"
        elif s.get("type") == "boolean":
            return r"(true|false)"
        elif s.get("type") == "null":
            return r"null"
        else:
            return r".*"

    return "^" + schema_to_regex(schema) + "$"


def print_cfg(productions: list[tuple[str, list[str]]]):
    for lhs, rhs in productions:
        print(f"{lhs} -> {' '.join(rhs)}")
