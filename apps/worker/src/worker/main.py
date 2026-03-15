from __future__ import annotations

import asyncio
import logging

from discursiva_domain.use_cases import CorrectSubmission
from discursiva_infra.postgres.pool import get_pool, close_pool
from discursiva_infra.postgres.submission_repo import PostgresSubmissionRepository
from discursiva_infra.s3.storage import S3Storage
from discursiva_infra.settings import get_settings
from discursiva_infra.sqs.queue import SQSQueue
from discursiva_infra.logging_config import setup_logging

setup_logging()
log = logging.getLogger(__name__)


async def run() -> None:
    pool     = await get_pool()
    repo     = PostgresSubmissionRepository(pool)
    storage  = S3Storage()
    queue    = SQSQueue()
    use_case = CorrectSubmission(repo=repo, storage=storage, queue=queue)
    settings = get_settings()

    log.info("Worker iniciado, aguardando mensagens em %s", settings.sqs_queue_url)

    try:
        while True:
            messages = await queue.receive(max_messages=5)

            if not messages:
                log.debug("Fila vazia, aguardando %ds...", settings.worker_poll_interval)
                await asyncio.sleep(settings.worker_poll_interval)
                continue

            # Um pequeno delay para simular o tempo de processamento
            await asyncio.sleep(5)
            tasks = [use_case.execute(msg) for msg in messages]
            await asyncio.gather(*tasks, return_exceptions=True)

    except asyncio.CancelledError:
        log.info("Worker interrompido.")
    finally:
        await close_pool(pool)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
