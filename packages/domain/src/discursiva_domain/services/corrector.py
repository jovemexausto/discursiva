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


def compute_score(text: str) -> Score:
    words = re.findall(r"\b\w+\b", text.lower())
    total = len(words)
    points = 0.0

    # 1. Comprimento
    if total >= 50:
        points += 2.0
    elif total >= 25:
        points += 1.0

    # 2. Parágrafos
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    if len(paragraphs) >= 3:
        points += 2.0
    elif len(paragraphs) >= 2:
        points += 1.0

    # 3. Vocabulário rico
    complex_words = [w for w in words if len(w) >= 7]
    if len(complex_words) >= 5:
        points += 2.0
    elif len(complex_words) >= 2:
        points += 1.0

    # 4. Pontuação
    punct = len(re.findall(r"[.!?,;:]", text))
    if punct >= 3:
        points += 2.0
    elif punct >= 1:
        points += 1.0

    # 5. Diversidade lexical
    if total > 0:
        top_freq = Counter(words).most_common(1)[0][1] / total
        if top_freq < 0.10:
            points += 2.0
        elif top_freq < 0.20:
            points += 1.0

    return Score(round(min(points, 10.0), 2))
