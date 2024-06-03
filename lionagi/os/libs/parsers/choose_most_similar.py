import numpy as np
from lionagi.os.libs.algorithms.jaro_distance import (
    jaro_winkler_similarity,
)


def choose_most_similar(word, correct_words_list, score_func=None):
    """
    Choose the most similar word from a list of correct words based on a
    similarity scoring function.

    Args:
        word (str): The word to compare.
        correct_words_list (list of str): The list of correct words to
            compare against.
        score_func (callable, optional): A function to compute the similarity
            score between two words. Defaults to jaro_winkler_similarity.

    Returns:
        str: The word from correct_words_list that is most similar to the
            input word based on the highest similarity score.
    """
    if correct_words_list is None or len(correct_words_list) == 0:
        return None

    if score_func is None:
        score_func = jaro_winkler_similarity

    scores = np.array(
        [
            score_func(str(word), str(correct_word))
            for correct_word in correct_words_list
        ]
    )

    max_score_index = np.argmax(scores)
    return correct_words_list[max_score_index]
