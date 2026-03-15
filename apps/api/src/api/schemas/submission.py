from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field


Status = Literal["PENDING", "PROCESSING", "DONE", "ERROR"]


class SubmissionCreateRequest(BaseModel):
    student_id : str = Field(..., min_length=1, max_length=100)
    text       : str = Field(..., min_length=1)


class SubmissionResponse(BaseModel):
    id         : str
    student_id : str
    s3_key     : str
    status     : Status
    score      : Optional[float]
    created_at : str
    updated_at : str


class SubmissionPageResponse(BaseModel):
    items         : list[SubmissionResponse]
    total         : int
    done_count    : int
    pending_count : int
    limit         : int
    offset        : int
