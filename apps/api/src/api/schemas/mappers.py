from discursiva_domain.entities import Submission
from api.schemas.submission import SubmissionResponse


def submission_to_response(s: Submission) -> SubmissionResponse:
    return SubmissionResponse(
        id         = str(s.id),
        student_id = s.student_id,
        s3_key     = s.s3_key,
        status     = s.status.value,
        score      = s.score.value if s.score is not None else None,
        created_at = s.created_at.isoformat(),
        updated_at = s.updated_at.isoformat(),
    )
