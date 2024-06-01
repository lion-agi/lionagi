def check_str_field(x, *args, fix_=True, **kwargs):
    if not isinstance(x, str):
        if fix_:
            try:
                return _fix_str_field(x, *args, **kwargs)
            except Exception as e:
                raise e

        raise ValueError(
            f"Default value for STRING must be a str, got {type(x).__name__}"
        )
    return x


def _fix_str_field(x):
    try:
        x = to_str(x)
        if isinstance(x, str):
            return x
        raise ValueError(f"Failed to convert {x} into a string value")
    except Exception as e:
        raise ValueError(f"Failed to convert {x} into a string value") from e


def choose_most_similar(word, correct_words_list, score_func=None):

    if score_func is None:
        score_func = StringMatch.jaro_winkler_similarity

    # Calculate Jaro-Winkler similarity scores for each potential match
    scores = np.array(
        [
            score_func(str(word), str(correct_word))
            for correct_word in correct_words_list
        ]
    )
    # Find the index of the highest score
    max_score_index = np.argmax(scores)
    return correct_words_list[max_score_index]
