from __future__ import annotations

import uuid
from datetime import timezone
from typing import Optional

import asyncpg

from discursiva_domain.entities import Submission, SubmissionStatus
from discursiva_domain.value_objects import Score, SubmissionId


class PostgresSubmissionRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def save(self, submission: Submission) -> None:
        await self._pool.execute(
            """
            INSERT INTO submissions (id, student_id, s3_key, status, score, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            uuid.UUID(str(submission.id)),
            submission.student_id,
            submission.s3_key,
            submission.status.value,
            submission.score.value if submission.score else None,
            submission.created_at,
            submission.updated_at,
        )

    async def get(self, id: SubmissionId) -> Optional[Submission]:
        row = await self._pool.fetchrow(
            "SELECT * FROM submissions WHERE id = $1",
            uuid.UUID(str(id)),
        )
        return self._to_entity(row) if row else None

    async def list_by_student(
        self, student_id: str, limit: int, offset: int
    ) -> tuple[list[Submission], int, int, int]:
        async with self._pool.acquire() as conn:
            counts = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status = 'DONE') as done_count,
                    COUNT(*) FILTER (WHERE status IN ('PENDING', 'PROCESSING')) as pending_count
                FROM submissions 
                WHERE student_id = $1
                """,
                student_id,
            )
            rows = await conn.fetch(
                """
                SELECT * FROM submissions
                WHERE student_id = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
                """,
                student_id, limit, offset,
            )
        return [self._to_entity(r) for r in rows], counts["total"], counts["done_count"], counts["pending_count"]

    async def update(self, submission: Submission) -> None:
        await self._pool.execute(
            """
            UPDATE submissions
            SET status = $1, score = $2, updated_at = $3
            WHERE id = $4
            """,
            submission.status.value,
            submission.score.value if submission.score else None,
            submission.updated_at,
            uuid.UUID(str(submission.id)),
        )

    @staticmethod
    def _to_entity(row: asyncpg.Record) -> Submission:
        return Submission(
            id=SubmissionId(value=row["id"]),
            student_id=row["student_id"],
            s3_key=row["s3_key"],
            status=SubmissionStatus(row["status"]),
            score=Score(float(row["score"])) if row["score"] is not None else None,
            created_at=row["created_at"].replace(tzinfo=timezone.utc),
            updated_at=row["updated_at"].replace(tzinfo=timezone.utc),
        )
