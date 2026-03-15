from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from discursiva_domain.value_objects import Score, SubmissionId


class SubmissionStatus(str, Enum):
    PENDING    = "PENDING"
    PROCESSING = "PROCESSING"
    DONE       = "DONE"
    ERROR      = "ERROR"


@dataclass
class Submission:
    id         : SubmissionId
    student_id : str
    s3_key     : str
    status     : SubmissionStatus = SubmissionStatus.PENDING
    score      : Optional[Score] = None
    created_at : datetime = field(default_factory=lambda:datetime.now(timezone.utc))
    updated_at : datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def mark_processing(self) -> None:
        if self.status != SubmissionStatus.PENDING:
            raise ValueError(f"Não é possível processar uma submissão no status {self.status}")
        self.status = SubmissionStatus.PROCESSING
        self.updated_at = datetime.now(timezone.utc)

    def mark_done(self, score: Score) -> None:
        if self.status != SubmissionStatus.PROCESSING:
            raise ValueError(f"Não é possível finalizar uma submissão no status {self.status}")
        self.status = SubmissionStatus.DONE
        self.score = score
        self.updated_at = datetime.now(timezone.utc)

    def mark_error(self) -> None:
        self.status = SubmissionStatus.ERROR
        self.updated_at = datetime.now(timezone.utc)
