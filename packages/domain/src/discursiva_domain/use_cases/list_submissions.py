from __future__ import annotations

from dataclasses import dataclass

from discursiva_domain.entities import Submission
from discursiva_domain.ports import SubmissionRepository


@dataclass
class ListSubmissionsQuery:
    student_id : str
    limit      : int = 20
    offset     : int = 0


@dataclass
class SubmissionPage:
    items         : list[Submission]
    total         : int
    done_count    : int
    pending_count : int
    limit         : int
    offset        : int


class ListSubmissions:
    def __init__(self, repo: SubmissionRepository) -> None:
        self._repo = repo

    async def execute(self, query: ListSubmissionsQuery) -> SubmissionPage:
        items, total, done, pending = await self._repo.list_by_student(
            student_id = query.student_id,
            limit      = query.limit,
            offset     = query.offset,
        )

        import asyncio
        await asyncio.sleep(1)

        return SubmissionPage(
            items         = items,
            total         = total,
            done_count    = done,
            pending_count = pending,
            limit         = query.limit,
            offset        = query.offset,
        )
