import unittest

from glossina.matcher import (
    dice_coefficient,
    levenshtein_distance,
    normalize_text,
    rank_matches,
    score_text,
)


class MatcherTests(unittest.TestCase):
    def test_normalize_text_collapses_whitespace_and_lowercases(self) -> None:
        self.assertEqual(normalize_text("  Hello\r\nWorld\n\tTest  "), "hello world test")

    def test_levenshtein_distance_basic_case(self) -> None:
        self.assertEqual(levenshtein_distance("kitten", "sitting"), 3)

    def test_dice_coefficient_identical_and_short_strings(self) -> None:
        self.assertEqual(dice_coefficient("abc", "abc"), 1.0)
        self.assertEqual(dice_coefficient("a", "a"), 1.0)
        self.assertEqual(dice_coefficient("a", "b"), 0.0)

    def test_score_text_returns_expected_keys_and_range(self) -> None:
        metrics = score_text("Apache License 2.0", "apache license 2.0")
        self.assertEqual(set(metrics.keys()), {"score", "dice", "lev_percent"})
        self.assertGreaterEqual(metrics["score"], 99.0)
        self.assertLessEqual(metrics["score"], 100.0)

    def test_rank_matches_filters_and_orders(self) -> None:
        corpus = [
            {"id": "A", "name": "A", "text": "alpha beta gamma", "category": "licenses", "reference": "a"},
            {"id": "B", "name": "B", "text": "alpha beta", "category": "licenses", "reference": "b"},
            {"id": "C", "name": "C", "text": "completely unrelated", "category": "licenses", "reference": "c"},
        ]

        matches = rank_matches("alpha beta", corpus, top=2, min_score=20.0)

        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0]["id"], "B")
        self.assertGreaterEqual(matches[0]["score"], matches[1]["score"])

    def test_rank_matches_empty_input_returns_no_results(self) -> None:
        self.assertEqual(rank_matches("  ", [{"text": "anything"}]), [])


if __name__ == "__main__":
    unittest.main()
