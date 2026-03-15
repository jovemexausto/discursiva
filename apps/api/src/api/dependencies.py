from __future__ import annotations

from typing import Annotated, AsyncGenerator

import asyncpg
from fastapi import Depends

from discursiva_domain.use_cases import GetSubmission, ListSubmissions, SubmitAnswer
from discursiva_infra.postgres.pool import get_pool, close_pool
from discursiva_infra.postgres.submission_repo import PostgresSubmissionRepository
from discursiva_infra.s3.storage import S3Storage
from discursiva_infra.sqs.queue import SQSQueue

_storage: S3Storage | None = None
_queue:   SQSQueue  | None = None


def _get_storage() -> S3Storage:
    global _storage
    if _storage is None:
        _storage = S3Storage()
    return _storage


def _get_queue() -> SQSQueue:
    global _queue
    if _queue is None:
        _queue = SQSQueue()
    return _queue


async def _get_pool() -> AsyncGenerator[asyncpg.Pool, None]:
    pool = await get_pool()
    try:
        yield pool
    finally:
        await close_pool(pool)


async def _get_repo(
    pool: Annotated[asyncpg.Pool, Depends(_get_pool)],
) -> PostgresSubmissionRepository:
    return PostgresSubmissionRepository(pool)


async def get_submit_answer(
    repo: Annotated[PostgresSubmissionRepository, Depends(_get_repo)],
) -> SubmitAnswer:
    return SubmitAnswer(repo=repo, storage=_get_storage(), queue=_get_queue())


async def get_get_submission(
    repo: Annotated[PostgresSubmissionRepository, Depends(_get_repo)],
) -> GetSubmission:
    return GetSubmission(repo=repo)


async def get_list_submissions(
    repo: Annotated[PostgresSubmissionRepository, Depends(_get_repo)],
) -> ListSubmissions:
    return ListSubmissions(repo=repo)
