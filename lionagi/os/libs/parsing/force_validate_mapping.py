import contextlib
from .parse_json import fuzzy_parse_json, md_to_json
from .force_validate_mapping_keys import force_validate_mapping_keys


def force_validate_dict(x, keys: dict | list[str]) -> dict:
    out_ = x

    if isinstance(out_, str):
        try:
            out_ = fuzzy_parse_json(out_)

        except:
            try:
                out_ = md_to_json(out_)

            except Exception:
                with contextlib.suppress(Exception):
                    out_ = fuzzy_parse_json(out_.replace("'", '"'))

    if isinstance(out_, dict):
        try:
            return force_validate_mapping_keys(keys, out_)
        except Exception as e:
            raise ValueError(f"Failed to force_validate_dict for input: {x}") from e
