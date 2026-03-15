"""Lambda handler — SQS event trigger for submission correction."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from discursiva_domain.ports import CorrectionMessage
from discursiva_domain.use_cases import CorrectSubmission
from discursiva_infra.postgres.pool import close_pool, get_pool
from discursiva_infra.postgres.submission_repo import PostgresSubmissionRepository
from discursiva_infra.s3.storage import S3Storage
from discursiva_infra.sqs.queue import SQSQueue

logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s [WORKER] %(levelname)s %(message)s",
    datefmt = "%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger(__name__)

_storage = S3Storage()
_queue   = SQSQueue()


async def _process(event: dict) -> None:
    pool = await get_pool()
    try:
        use_case = CorrectSubmission(
            repo=PostgresSubmissionRepository(pool),
            storage=_storage,
            queue=_queue,
        )
        for record in event.get("Records", []):
            body = json.loads(record["body"])
            msg  = CorrectionMessage(
                submission_id  = body["submission_id"],
                s3_key         = body["s3_key"],
                receipt_handle = record.get("receiptHandle", ""),
            )
            log.info("Processing submission %s", msg.submission_id)
            await use_case.execute(msg)
    finally:
        await close_pool(pool)


def process(event: dict, context: Any) -> dict:
    """Entry point for AWS Lambda / LocalStack."""
    asyncio.run(_process(event))
    return {"statusCode": 200}
