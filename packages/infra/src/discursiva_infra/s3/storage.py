from __future__ import annotations

import asyncio
from functools import partial

import boto3

from discursiva_infra.settings import settings


class S3Storage:
    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url          = settings.s3_endpoint_url,
            aws_access_key_id     = settings.aws_access_key_id,
            aws_secret_access_key = settings.aws_secret_access_key,
            region_name           = settings.aws_region,
        )
        self._bucket = settings.s3_bucket

    async def upload(self, key: str, content: str) -> str:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            partial(
                self._client.put_object,
                Bucket      = self._bucket,
                Key         = key,
                Body        = content.encode("utf-8"),
                ContentType = "text/plain; charset=utf-8",
            ),
        )
        return key

    async def download(self, key: str) -> str:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            partial(self._client.get_object, Bucket=self._bucket, Key=key),
        )
        return response["Body"].read().decode("utf-8")
