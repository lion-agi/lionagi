import numpy as np
from ..algorithms.jaro_distance import jaro_winkler_similarity


def force_validate_mapping_keys(keys: dict | list[str], dict_, score_func=None):
    if score_func is None:
        score_func = jaro_winkler_similarity

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
