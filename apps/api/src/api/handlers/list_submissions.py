from __future__ import annotations

import asyncio
import logging
from typing import Any

from discursiva_domain.use_cases import ListSubmissions, ListSubmissionsQuery
from discursiva_infra.logging_config import setup_logging
from discursiva_infra.postgres.pool import close_pool, get_pool
from discursiva_infra.postgres.submission_repo import PostgresSubmissionRepository
from ..utils import response, serialize

setup_logging()
log = logging.getLogger(__name__)

async def _handler(event: dict) -> dict:
    params     = event.get("queryStringParameters") or {}
    student_id = params.get("student_id", "").strip()

    if not student_id:
        return response(422, {"detail": "parâmetro student_id é obrigatório"})

    limit  = max(1, min(100, int(params.get("limit",  "20"))))
    offset = max(0,          int(params.get("offset", "0")))

    pool = await get_pool()
    try:
        page = await ListSubmissions(
            repo=PostgresSubmissionRepository(pool)
        ).execute(ListSubmissionsQuery(student_id=student_id, limit=limit, offset=offset))
        return response(200, {
            "items":  [serialize(s) for s in page.items],
            "total":  page.total,
            "limit":  page.limit,
            "offset": page.offset,
        })
    finally:
        await close_pool(pool)

def handler(event: dict, context: Any) -> dict:
    return asyncio.run(_handler(event))
