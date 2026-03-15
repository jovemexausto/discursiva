from __future__ import annotations

import asyncio
import logging
from typing import Any

from discursiva_domain.use_cases import GetSubmission, GetSubmissionQuery, SubmissionNotFound
from discursiva_infra.logging_config import setup_logging
from discursiva_infra.postgres.pool import close_pool, get_pool
from discursiva_infra.postgres.submission_repo import PostgresSubmissionRepository
from ..utils import response, serialize

setup_logging()
log = logging.getLogger(__name__)

async def _handler(event: dict) -> dict:
    submission_id = (event.get("pathParameters") or {}).get("id", "")

    pool = await get_pool()
    try:
        submission = await GetSubmission(
            repo=PostgresSubmissionRepository(pool)
        ).execute(GetSubmissionQuery(submission_id=submission_id))
        return response(200, serialize(submission))
    except SubmissionNotFound as exc:
        return response(404, {"detail": str(exc)})
    finally:
        await close_pool(pool)

def handler(event: dict, context: Any) -> dict:
    return asyncio.run(_handler(event))
