def correct_dict_keys(keys: dict | list[str], dict_, score_func=None):
    if score_func is None:
        score_func = StringMatch.jaro_winkler_similarity

    fields_set = set(keys if isinstance(keys, list) else keys.keys())
    corrected_out = {}
    used_keys = set()

    for k, v in dict_.items():
        if k in fields_set:
            corrected_out[k] = v
            fields_set.remove(k)  # Remove the matched key
            used_keys.add(k)
        else:
            # Calculate Jaro-Winkler similarity scores for each potential match
            scores = np.array([score_func(k, field) for field in fields_set])
            # Find the index of the highest score
            max_score_index = np.argmax(scores)
            # Select the best match based on the highest score
            best_match = list(fields_set)[max_score_index]

            corrected_out[best_match] = v
            fields_set.remove(best_match)  # Remove the matched key
            used_keys.add(best_match)

    if len(used_keys) < len(dict_):
        for k, v in dict_.items():
            if k not in used_keys:
                corrected_out[k] = v

    return corrected_out


def check_dict_field(x, keys: list[str] | dict, fix_=True, **kwargs):
    if isinstance(x, dict):
        return x
    if fix_:
        try:
            x = to_str(x)
            return StringMatch.force_validate_dict(x, keys=keys, **kwargs)
        except Exception as e:
            raise ValueError("Invalid dict field type.") from e
    raise ValueError(f"Default value for DICT must be a dict, got {type(x).__name__}")


def force_validate_dict(x, keys: dict | list[str]) -> dict:
    out_ = x

    if isinstance(out_, str):
        # first try to parse it straight as a fuzzy json

        try:
            out_ = ParseUtil.fuzzy_parse_json(out_)
            return StringMatch.correct_dict_keys(keys, out_)

        except:
            try:
                out_ = ParseUtil.md_to_json(out_)
                return StringMatch.correct_dict_keys(keys, out_)

            except Exception:
                try:
                    # if failed we try to extract the json block and parse it
                    out_ = ParseUtil.md_to_json(out_)
                    return StringMatch.correct_dict_keys(keys, out_)

                except Exception:
                    # if still failed we try to extract the json block using re and parse it again
                    match = re.search(r"```json\n({.*?})\n```", out_, re.DOTALL)
                    if match:
                        out_ = match.group(1)
                        try:
                            out_ = ParseUtil.fuzzy_parse_json(out_)
                            return StringMatch.correct_dict_keys(keys, out_)

                        except:
                            try:
                                out_ = ParseUtil.fuzzy_parse_json(
                                    out_.replace("'", '"')
                                )
                                return StringMatch.correct_dict_keys(keys, out_)
                            except:
                                pass

    if isinstance(out_, dict):
        try:
            return StringMatch.correct_dict_keys(keys, out_)
        except Exception as e:
            raise ValueError(f"Failed to force_validate_dict for input: {x}") from e
