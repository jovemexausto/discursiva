from typing import Protocol, Optional
from discursiva_domain.entities import Submission
from discursiva_domain.value_objects import SubmissionId


class SubmissionRepository(Protocol):
    async def save(self, submission: Submission) -> None: ...
    async def get(self, id: SubmissionId) -> Optional[Submission]: ...
    async def list_by_student(
        self,
        student_id: str,
        limit: int,
        offset: int,
    ) -> tuple[list[Submission], int, int, int]: ...
    async def update(self, submission: Submission) -> None: ...
