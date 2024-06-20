import unittest
from lionagi.lib.algorithms.jaro_distance import (
    jaro_distance,
    jaro_winkler_similarity,
)
from lionagi.lib.algorithms.levenshtein_distance import levenshtein_distance


class TestStringSimilarity(unittest.TestCase):

    def test_jaro_distance(self):
        self.assertAlmostEqual(jaro_distance("MARTHA", "MARHTA"), 0.9444444444444445)
        self.assertAlmostEqual(jaro_distance("DWAYNE", "DUANE"), 0.8222222222222223)
        self.assertAlmostEqual(jaro_distance("DIXON", "DICKSONX"), 0.7666666666666666)
        self.assertAlmostEqual(jaro_distance("", ""), 1.0)
        self.assertAlmostEqual(jaro_distance("a", ""), 0.0)
        self.assertAlmostEqual(jaro_distance("", "a"), 0.0)
        self.assertAlmostEqual(jaro_distance("abc", "abc"), 1.0)

    def test_jaro_winkler_similarity(self):
        self.assertAlmostEqual(
            jaro_winkler_similarity("MARTHA", "MARHTA"), 0.9611111111111111
        )
        self.assertAlmostEqual(jaro_winkler_similarity("DWAYNE", "DUANE"), 0.84)
        self.assertAlmostEqual(
            jaro_winkler_similarity("DIXON", "DICKSONX"), 0.8133333333333332
        )
        self.assertAlmostEqual(jaro_winkler_similarity("", ""), 1.0)
        self.assertAlmostEqual(jaro_winkler_similarity("a", ""), 0.0)
        self.assertAlmostEqual(jaro_winkler_similarity("", "a"), 0.0)
        self.assertAlmostEqual(jaro_winkler_similarity("abc", "abc"), 1.0)


class TestLevenshteinDistance(unittest.TestCase):

    def test_levenshtein_distance(self):
        self.assertEqual(levenshtein_distance("kitten", "sitting"), 3)
        self.assertEqual(levenshtein_distance("flaw", "lawn"), 2)
        self.assertEqual(levenshtein_distance("intention", "execution"), 5)
        self.assertEqual(levenshtein_distance("", ""), 0)
        self.assertEqual(levenshtein_distance("a", ""), 1)
        self.assertEqual(levenshtein_distance("", "a"), 1)

    def test_levenshtein_distance2(self):
        """Test Levenshtein distance calculations."""
        self.assertEqual(levenshtein_distance("kitten", "sitting"), 3)
        self.assertEqual(levenshtein_distance("", ""), 0)
        self.assertEqual(levenshtein_distance("book", "back"), 2)
        self.assertEqual(levenshtein_distance("book", ""), 4)
        self.assertEqual(levenshtein_distance("", "back"), 4)


if __name__ == "__main__":
    unittest.main(argv=[""], verbosity=2, exit=False)
