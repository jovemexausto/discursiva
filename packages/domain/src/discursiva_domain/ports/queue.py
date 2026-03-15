from typing import Protocol
from dataclasses import dataclass


@dataclass(frozen=True)
class CorrectionMessage:
    submission_id  : str
    s3_key         : str
    receipt_handle : str


class QueuePort(Protocol):
    async def publish(self, submission_id: str, s3_key: str) -> None: ...
    async def receive(self, max_messages: int = 5) -> list[CorrectionMessage]: ...
    async def delete(self, receipt_handle: str) -> None: ...
