from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from discursiva_domain.use_cases import SubmitAnswer, SubmitAnswerCommand
from discursiva_infra.logging_config import setup_logging
from discursiva_infra.postgres.pool import close_pool, get_pool
from discursiva_infra.postgres.submission_repo import PostgresSubmissionRepository
from discursiva_infra.s3.storage import S3Storage
from discursiva_infra.sqs.queue import SQSQueue
from ..utils import response, serialize

setup_logging()
log = logging.getLogger(__name__)

_storage: S3Storage | None = None
_queue:   SQSQueue  | None = None

async def _handler(event: dict) -> dict:
    global _storage, _queue
    
    body       = json.loads(event.get("body") or "{}")
    student_id = body.get("student_id", "").strip()
    text       = body.get("text", "").strip()

    if not student_id or not text:
        return response(422, {"detail": "student_id e text são obrigatórios"})

    if _storage is None:
        _storage = S3Storage()
    if _queue is None:
        _queue = SQSQueue()

    pool = await get_pool()
    try:
        submission  = await SubmitAnswer(
            repo    = PostgresSubmissionRepository(pool),
            storage = _storage,
            queue   = _queue,
        ).execute(SubmitAnswerCommand(student_id=student_id, text=text))
        
        return response(201, serialize(submission))
    finally:
        await close_pool(pool)

def handler(event: dict, context: Any) -> dict:
    return asyncio.run(_handler(event))
