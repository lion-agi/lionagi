import numpy as np
from ..algorithms.jaro_distance import jaro_winkler_similarity


def choose_most_similar(word, correct_words_list, score_func=None):

    if score_func is None:
        score_func = jaro_winkler_similarity

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
