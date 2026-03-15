from __future__ import annotations

from dataclasses import dataclass

from discursiva_domain.entities import Submission
from discursiva_domain.ports import QueuePort, StoragePort, SubmissionRepository
from discursiva_domain.value_objects import SubmissionId


@dataclass
class SubmitAnswerCommand:
    student_id : str
    text       : str


class SubmitAnswer:
    def __init__(
        self,
        repo    : SubmissionRepository,
        storage : StoragePort,
        queue   : QueuePort,
    ) -> None:
        self._repo    = repo
        self._storage = storage
        self._queue   = queue

    async def execute(self, cmd: SubmitAnswerCommand) -> Submission:
        submission_id = SubmissionId.generate()
        s3_key = f"submissions/{submission_id}.txt"

        await self._storage.upload(s3_key, cmd.text)

        submission = Submission(
            id         = submission_id,
            student_id = cmd.student_id,
            s3_key     = s3_key,
        )
        await self._repo.save(submission)
        await self._queue.publish(str(submission_id), s3_key)

        return submission
