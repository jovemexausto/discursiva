"""
Lógica de scoring.

Cinco critérios ortogonais, cada um valendo até 2 pontos (máximo 10):
  1. Comprimento         — >= 50 palavras
  2. Parágrafos          — >= 3 parágrafos
  3. Vocabulário rico    — >= 5 palavras com 7+ letras
  4. Pontuação adequada  — >= 3 sinais de pontuação
  5. Diversidade lexical — palavra mais frequente < 10% do total
"""

from __future__ import annotations

import re
from collections import Counter

from discursiva_domain.value_objects import Score


def _score_length(total_words: int) -> float:
    if total_words >= 50:
        return 2.0
    if total_words >= 25:
        return 1.0
    return 0.0


def _score_paragraphs(text: str) -> float:
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    num_paragraphs = len(paragraphs)
    if num_paragraphs >= 3:
        return 2.0
    if num_paragraphs >= 2:
        return 1.0
    return 0.0


def _score_vocabulary(words: list[str]) -> float:
    complex_words = [w for w in words if len(w) >= 7]
    num_complex = len(complex_words)
    if num_complex >= 5:
        return 2.0
    if num_complex >= 2:
        return 1.0
    return 0.0


def _score_punctuation(text: str) -> float:
    punct = len(re.findall(r"[.!?,;:]", text))
    if punct >= 3:
        return 2.0
    if punct >= 1:
        return 1.0
    return 0.0


def _score_lexical_diversity(words: list[str], total_words: int) -> float:
    if total_words == 0:
        return 0.0
    top_freq = Counter(words).most_common(1)[0][1] / total_words
    if top_freq < 0.10:
        return 2.0
    if top_freq < 0.20:
        return 1.0
    return 0.0


def compute_score(text: str) -> Score:
    words = re.findall(r"\b\w+\b", text.lower())
    total_words = len(words)
    points = sum([
        _score_length(total_words),
        _score_paragraphs(text),
        _score_vocabulary(words),
        _score_punctuation(text),
        _score_lexical_diversity(words, total_words),
    ])

    return Score(round(min(points, 10.0), 2))
