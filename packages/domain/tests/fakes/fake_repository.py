from __future__ import annotations

from discursiva_domain.entities import Submission
from discursiva_domain.ports import SubmissionRepository
from discursiva_domain.value_objects import SubmissionId


class FakeSubmissionRepository(SubmissionRepository):
    def __init__(self) -> None:
        self._store: dict[str, Submission] = {}

    async def save(self, submission: Submission) -> None:
        self._store[str(submission.id)] = submission

    async def get(self, id: SubmissionId) -> Submission | None:
        return self._store.get(str(id))

    async def list_by_student(
        self, student_id: str, limit: int, offset: int
    ) -> tuple[list[Submission], int]:
        matches = [
            s for s in self._store.values() if s.student_id == student_id
        ]
        matches.sort(key=lambda s: s.created_at, reverse=True)
        return matches[offset : offset + limit], len(matches)

    async def update(self, submission: Submission) -> None:
        self._store[str(submission.id)] = submission
