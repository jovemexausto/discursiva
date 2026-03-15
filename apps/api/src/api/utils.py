import json

def response(status: int, body: dict | list) -> dict:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, default=str),
    }

def serialize(s) -> dict:
    return {
        "id":         str(s.id),
        "student_id": s.student_id,
        "s3_key":     s.s3_key,
        "status":     s.status.value,
        "score":      s.score.value if s.score is not None else None,
        "created_at": s.created_at.isoformat(),
        "updated_at": s.updated_at.isoformat(),
    }
