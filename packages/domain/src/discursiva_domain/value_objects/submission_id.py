from __future__ import annotations
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class SubmissionId:
    value: uuid.UUID

    @classmethod
    def generate(cls) -> SubmissionId:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_str(cls, raw: str) -> SubmissionId:
        return cls(value=uuid.UUID(raw))

    def __str__(self) -> str:
        return str(self.value)
