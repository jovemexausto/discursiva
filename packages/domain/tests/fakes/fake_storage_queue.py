from __future__ import annotations

from discursiva_domain.ports import CorrectionMessage


class FakeStorage:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    async def upload(self, key: str, content: str) -> str:
        self._store[key] = content
        return key

    async def download(self, key: str) -> str:
        if key not in self._store:
            raise FileNotFoundError(key)
        return self._store[key]


class FakeQueue:
    def __init__(self) -> None:
        self._messages: list[CorrectionMessage] = []
        self.published: list[dict[str, str]] = []

    async def publish(self, submission_id: str, s3_key: str) -> None:
        msg = CorrectionMessage(
            submission_id=submission_id,
            s3_key=s3_key,
            receipt_handle=f"receipt-{submission_id}",
        )
        self._messages.append(msg)
        self.published.append({"submission_id": submission_id, "s3_key": s3_key})

    async def receive(self, max_messages: int = 5) -> list[CorrectionMessage]:
        batch, self._messages = self._messages[:max_messages], self._messages[max_messages:]
        return batch

    async def delete(self, receipt_handle: str) -> None:
        self._messages = [m for m in self._messages if m.receipt_handle != receipt_handle]
