from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from discursiva_domain.use_cases import (
    GetSubmission,
    ListSubmissions,
    SubmitAnswer,
    SubmitAnswerCommand,
    GetSubmissionQuery,
    ListSubmissionsQuery,
    SubmissionNotFound,
)
from api.dependencies import get_get_submission, get_list_submissions, get_submit_answer
from api.schemas import (
    SubmissionCreateRequest,
    SubmissionPageResponse,
    SubmissionResponse,
    submission_to_response,
)

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("", response_model=SubmissionResponse, status_code=201)
async def create_submission(
    body: SubmissionCreateRequest,
    use_case: Annotated[SubmitAnswer, Depends(get_submit_answer)],
) -> SubmissionResponse:
    submission = await use_case.execute(
        SubmitAnswerCommand(student_id=body.student_id, text=body.text)
    )
    return submission_to_response(submission)


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: str,
    use_case: Annotated[GetSubmission, Depends(get_get_submission)],
) -> SubmissionResponse:
    try:
        submission = await use_case.execute(GetSubmissionQuery(submission_id=submission_id))
    except SubmissionNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return submission_to_response(submission)


@router.get("", response_model=SubmissionPageResponse)
async def list_submissions(
    use_case: Annotated[ListSubmissions, Depends(get_list_submissions)],
    student_id: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> SubmissionPageResponse:
    page = await use_case.execute(
        ListSubmissionsQuery(student_id=student_id, limit=limit, offset=offset)
    )
    return SubmissionPageResponse(
        items         = [submission_to_response(s) for s in page.items],
        total         = page.total,
        done_count    = page.done_count,
        pending_count = page.pending_count,
        limit         = page.limit,
        offset        = page.offset,
    )
