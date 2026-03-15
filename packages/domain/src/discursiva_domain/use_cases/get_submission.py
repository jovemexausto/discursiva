from __future__ import annotations

from dataclasses import dataclass

from discursiva_domain.entities import Submission
from discursiva_domain.ports import SubmissionRepository
from discursiva_domain.value_objects import SubmissionId


class SubmissionNotFound(Exception):
    def __init__(self, submission_id: str) -> None:
        super().__init__(f"Submission {submission_id!r} not found")


@dataclass
class GetSubmissionQuery:
    submission_id: str


class GetSubmission:
    def __init__(self, repo: SubmissionRepository) -> None:
        self._repo = repo

    async def execute(self, query: GetSubmissionQuery) -> Submission:
        try:
            sid = SubmissionId.from_str(query.submission_id)
        except ValueError:
            raise SubmissionNotFound(query.submission_id)

        submission = await self._repo.get(sid)
        if submission is None:
            raise SubmissionNotFound(query.submission_id)

        return submission
