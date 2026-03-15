from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Score:
    value: float

    def __post_init__(self) -> None:
        if not (0.0 <= self.value <= 10.0):
            raise ValueError(f"A nota deve estar entre 0 e 10, valor recebido: {self.value}")

    def __str__(self) -> str:
        return f"{self.value:.2f}"
