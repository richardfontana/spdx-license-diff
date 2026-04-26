"""Similarity scoring and ranking for SPDX text matching."""

from collections import Counter
from typing import Iterable


def normalize_text(text: str) -> str:
    return " ".join(text.replace("\r\n", "\n").split()).strip().lower()


def levenshtein_distance(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    if len(a) > len(b):
        a, b = b, a

    previous = list(range(len(a) + 1))
    for i, cb in enumerate(b, start=1):
        current = [i]
        for j, ca in enumerate(a, start=1):
            insertions = previous[j] + 1
            deletions = current[j - 1] + 1
            substitutions = previous[j - 1] + (ca != cb)
            current.append(min(insertions, deletions, substitutions))
        previous = current

    return previous[-1]


def dice_coefficient(a: str, b: str) -> float:
    if a == b:
        return 1.0
    if len(a) < 2 or len(b) < 2:
        return 0.0

    bigrams_a = Counter(a[i : i + 2] for i in range(len(a) - 1))
    bigrams_b = Counter(b[i : i + 2] for i in range(len(b) - 1))

    overlap = sum((bigrams_a & bigrams_b).values())
    total = sum(bigrams_a.values()) + sum(bigrams_b.values())
    return (2.0 * overlap) / total if total else 0.0


def score_text(input_text: str, candidate_text: str) -> dict[str, float]:
    normalized_input = normalize_text(input_text)
    normalized_candidate = normalize_text(candidate_text)

    max_len = max(len(normalized_input), len(normalized_candidate), 1)
    lev_distance = levenshtein_distance(normalized_input, normalized_candidate)
    lev_percent = (1 - (lev_distance / max_len)) * 100
    dice_percent = dice_coefficient(normalized_input, normalized_candidate) * 100
    score = (dice_percent * 0.6) + (lev_percent * 0.4)

    return {
        "score": score,
        "dice": dice_percent,
        "lev_percent": lev_percent,
    }


def rank_matches(input_text: str, corpus: Iterable[dict], top: int = 10, min_score: float = 25.0) -> list[dict]:
    trimmed = input_text.strip()
    if not trimmed:
        return []

    matches = []
    for entry in corpus:
        metrics = score_text(trimmed, entry["text"])
        ranked = {
            **entry,
            **metrics,
        }
        if ranked["score"] >= min_score:
            matches.append(ranked)

    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches[:top]
