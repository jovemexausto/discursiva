from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from discursiva_domain.use_cases import (
    GetSubmission,
    GetSubmissionQuery,
    ListSubmissions,
    ListSubmissionsQuery,
    SubmitAnswer,
    SubmitAnswerCommand,
    SubmissionNotFound,
)
from discursiva_infra.postgres.pool import close_pool, get_pool
from discursiva_infra.postgres.submission_repo import PostgresSubmissionRepository
from discursiva_infra.s3.storage import S3Storage
from discursiva_infra.sqs.queue import SQSQueue
from discursiva_infra.logging_config import setup_logging

setup_logging()
log = logging.getLogger(__name__)

_storage = S3Storage()
_queue   = SQSQueue()


def _response(status: int, body: dict | list) -> dict:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, default=str),
    }


def _serialize(s) -> dict:
    return {
        "id":         str(s.id),
        "student_id": s.student_id,
        "s3_key":     s.s3_key,
        "status":     s.status.value,
        "score":      s.score.value if s.score is not None else None,
        "created_at": s.created_at.isoformat(),
        "updated_at": s.updated_at.isoformat(),
    }


async def _create(event: dict) -> dict:
    body       = json.loads(event.get("body") or "{}")
    student_id = body.get("student_id", "").strip()
    text       = body.get("text", "").strip()

    if not student_id or not text:
        return _response(422, {"detail": "student_id and text are required"})

    pool = await get_pool()
    try:
        submission = await SubmitAnswer(
            repo=PostgresSubmissionRepository(pool),
            storage=_storage,
            queue=_queue,
        ).execute(SubmitAnswerCommand(student_id=student_id, text=text))
        return _response(201, _serialize(submission))
    finally:
        await close_pool(pool)


def create(event: dict, context: Any) -> dict:
    return asyncio.run(_create(event))


async def _get_by_id(event: dict) -> dict:
    submission_id = (event.get("pathParameters") or {}).get("id", "")

    pool = await get_pool()
    try:
        submission = await GetSubmission(
            repo=PostgresSubmissionRepository(pool)
        ).execute(GetSubmissionQuery(submission_id=submission_id))
        return _response(200, _serialize(submission))
    except SubmissionNotFound as exc:
        return _response(404, {"detail": str(exc)})
    finally:
        await close_pool(pool)


def get_by_id(event: dict, context: Any) -> dict:
    return asyncio.run(_get_by_id(event))


async def _list_by_student(event: dict) -> dict:
    params     = event.get("queryStringParameters") or {}
    student_id = params.get("student_id", "").strip()

    if not student_id:
        return _response(422, {"detail": "student_id query param is required"})

    limit  = max(1, min(100, int(params.get("limit",  "20"))))
    offset = max(0,          int(params.get("offset", "0")))

    pool = await get_pool()
    try:
        page = await ListSubmissions(
            repo=PostgresSubmissionRepository(pool)
        ).execute(ListSubmissionsQuery(student_id=student_id, limit=limit, offset=offset))
        return _response(200, {
            "items":  [_serialize(s) for s in page.items],
            "total":  page.total,
            "limit":  page.limit,
            "offset": page.offset,
        })
    finally:
        await close_pool(pool)


def list_by_student(event: dict, context: Any) -> dict:
    return asyncio.run(_list_by_student(event))
