// SPDX-FileCopyrightText: SPDX-License-Diff contributors
// SPDX-License-Identifier: GPL-3.0-or-later

import { distance as levenshteinDistance } from 'fastest-levenshtein';
import diceCoefficient from 'fast-dice-coefficient';

function normalizeText(text) {
  return text
    .replace(/\r\n/g, '\n')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase();
}

function scoreText(input, candidate) {
  const normalizedInput = normalizeText(input);
  const normalizedCandidate = normalizeText(candidate);

  const maxLen = Math.max(normalizedInput.length, normalizedCandidate.length) || 1;
  const levDistance = levenshteinDistance(normalizedInput, normalizedCandidate);
  const levPercent = (1 - (levDistance / maxLen)) * 100;
  const dice = diceCoefficient(normalizedInput, normalizedCandidate) * 100;

  const score = (dice * 0.6) + (levPercent * 0.4);

  return {
    score,
    dice,
    levPercent
  };
}

export function rankMatches(inputText, corpus, { top = 10, minScore = 25 } = {}) {
  const trimmedInput = inputText.trim();
  if (!trimmedInput) {
    return [];
  }

  return corpus
    .map((entry) => {
      const metrics = scoreText(trimmedInput, entry.text);
      return {
        ...entry,
        ...metrics
      };
    })
    .filter((entry) => entry.score >= minScore)
    .sort((a, b) => b.score - a.score)
    .slice(0, top);
}
