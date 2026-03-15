from __future__ import annotations

import logging

from discursiva_domain.ports import QueuePort, StoragePort, SubmissionRepository, CorrectionMessage
from discursiva_domain.services import compute_score
from discursiva_domain.value_objects import SubmissionId

log = logging.getLogger(__name__)


class CorrectSubmission:
    def __init__(
        self,
        repo    : SubmissionRepository,
        storage : StoragePort,
        queue   : QueuePort,
    ) -> None:
        self._repo    = repo
        self._storage = storage
        self._queue   = queue

    async def execute(self, message: CorrectionMessage) -> None:
        sid = SubmissionId.from_str(message.submission_id)
        submission = await self._repo.get(sid)

        if submission is None:
            log.warning("Submission %s not found, skipping", message.submission_id)
            await self._queue.delete(message.receipt_handle)
            return

        # Idempotência: se já foi processada por outro worker, descarta
        if submission.status.value != "PENDING":
            log.warning(
                "Submission %s already in status %s, skipping",
                message.submission_id,
                submission.status,
            )
            await self._queue.delete(message.receipt_handle)
            return

        try:
            submission.mark_processing()
            await self._repo.update(submission)

            text = await self._storage.download(submission.s3_key)
            score = compute_score(text)

            submission.mark_done(score)
            await self._repo.update(submission)

            await self._queue.delete(message.receipt_handle)
            log.info("Submission %s corrected — score: %s", message.submission_id, score)

        except Exception:
            submission.mark_error()
            await self._repo.update(submission)
            log.exception("Failed to correct submission %s", message.submission_id)
            # Não deleta a mensagem, volta à fila para retry / DLQ
