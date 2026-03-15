from __future__ import annotations

import asyncio
import json
from functools import partial

import boto3

from discursiva_domain.ports import CorrectionMessage
from discursiva_infra.settings import settings


class SQSQueue:
    def __init__(self) -> None:
        self._client = boto3.client(
            "sqs",
            endpoint_url          = settings.sqs_endpoint_url,
            aws_access_key_id     = settings.aws_access_key_id,
            aws_secret_access_key = settings.aws_secret_access_key,
            region_name           = settings.aws_region,
        )
        self._queue_url = settings.sqs_queue_url

    async def publish(self, submission_id: str, s3_key: str) -> None:
        body = json.dumps({"submission_id": submission_id, "s3_key": s3_key})
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            partial(self._client.send_message, QueueUrl=self._queue_url, MessageBody=body),
        )

    async def receive(self, max_messages: int = 5) -> list[CorrectionMessage]:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            partial(
                self._client.receive_message,
                QueueUrl=self._queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=5,
            ),
        )
        messages = []
        for msg in response.get("Messages", []):
            #
            body_str = msg.get("Body")
            receipt  = msg.get("ReceiptHandle")
            
            if not body_str or not receipt:
                continue

            body = json.loads(body_str)
            messages.append(
                CorrectionMessage(
                    submission_id  = body["submission_id"],
                    s3_key         = body["s3_key"],
                    receipt_handle = receipt,
                )
            )
        return messages

    async def delete(self, receipt_handle: str) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            partial(
                self._client.delete_message,
                QueueUrl=self._queue_url,
                ReceiptHandle=receipt_handle,
            ),
        )
