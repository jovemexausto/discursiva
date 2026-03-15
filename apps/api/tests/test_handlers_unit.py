import json
import pytest
from unittest.mock import patch

from tests.fakes import FakeQueue, FakeStorage, FakeSubmissionRepository  # type: ignore

from api.handlers import create_submission, get_submission, list_submissions


@pytest.fixture
def fakes():
    return FakeSubmissionRepository(), FakeStorage(), FakeQueue()

@pytest.fixture
def mock_dependencies(fakes):
    repo, storage, queue = fakes

    async def mock_get_pool():
        return None

    # Mocka as dependências dos handlers
    with patch("api.handlers.create_submission.get_pool", new=mock_get_pool), \
         patch("api.handlers.get_submission.get_pool", new=mock_get_pool), \
         patch("api.handlers.list_submissions.get_pool", new=mock_get_pool), \
         patch("api.handlers.create_submission.close_pool"), \
         patch("api.handlers.get_submission.close_pool"), \
         patch("api.handlers.list_submissions.close_pool"), \
         patch("api.handlers.create_submission.PostgresSubmissionRepository", return_value=repo), \
         patch("api.handlers.get_submission.PostgresSubmissionRepository", return_value=repo), \
         patch("api.handlers.list_submissions.PostgresSubmissionRepository", return_value=repo), \
         patch("api.handlers.create_submission._storage", storage), \
         patch("api.handlers.create_submission._queue", queue), \
         patch("discursiva_infra.s3.storage.S3Storage", return_value=storage), \
         patch("discursiva_infra.sqs.queue.SQSQueue", return_value=queue):
        
        # Define os globais para os testes
        from api.handlers import create_submission
        create_submission._storage = storage
        create_submission._queue = queue
        
        yield fakes


def test_create_returns_201(mock_dependencies):
    event = {"body": json.dumps({"student_id": "s1", "text": "texto"})}
    resp = create_submission.handler(event, {})
    assert resp["statusCode"] == 201
    data = json.loads(resp["body"])
    assert data["student_id"] == "s1"
    assert data["status"] == "PENDING"
    assert data["score"] is None
    assert "id" in data


def test_create_missing_text_returns_422(mock_dependencies):
    event = {"body": json.dumps({"student_id": "s1"})}
    resp = create_submission.handler(event, {})
    assert resp["statusCode"] == 422


def test_create_empty_student_id_returns_422(mock_dependencies):
    event = {"body": json.dumps({"student_id": "", "text": "texto"})}
    resp = create_submission.handler(event, {})
    assert resp["statusCode"] == 422


def test_get_existing_submission(mock_dependencies):
    # Cria uma submissão
    event_create = {"body": json.dumps({"student_id": "s1", "text": "t"})}
    create_resp = create_submission.handler(event_create, {})
    sid = json.loads(create_resp["body"])["id"]
    
    # Pega a submissão
    event_get = {"pathParameters": {"id": sid}}
    resp = get_submission.handler(event_get, {})
    assert resp["statusCode"] == 200
    assert json.loads(resp["body"])["id"] == sid


def test_get_nonexistent_returns_404(mock_dependencies):
    import uuid
    event_get = {"pathParameters": {"id": str(uuid.uuid4())}}
    resp = get_submission.handler(event_get, {})
    assert resp["statusCode"] == 404


def test_get_invalid_id_returns_404(mock_dependencies):
    event_get = {"pathParameters": {"id": "not-a-uuid"}}
    resp = get_submission.handler(event_get, {})
    assert resp["statusCode"] == 404


def test_list_returns_all_for_student(mock_dependencies):
    for i in range(3):
        create_submission.handler({"body": json.dumps({"student_id": "s2", "text": f"t{i}"})}, {})
        
    event_list = {"queryStringParameters": {"student_id": "s2"}}
    resp = list_submissions.handler(event_list, {})
    assert resp["statusCode"] == 200
    data = json.loads(resp["body"])
    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_list_pagination(mock_dependencies):
    for i in range(5):
        create_submission.handler({"body": json.dumps({"student_id": "s3", "text": f"t{i}"})}, {})
        
    event_list = {"queryStringParameters": {"student_id": "s3", "limit": "2", "offset": "0"}}
    resp = list_submissions.handler(event_list, {})
    data = json.loads(resp["body"])
    assert data["total"] == 5
    assert len(data["items"]) == 2


def test_list_missing_student_id_returns_422(mock_dependencies):
    event_list = {}
    resp = list_submissions.handler(event_list, {})
    assert resp["statusCode"] == 422


def test_list_empty_student_returns_empty_page(mock_dependencies):
    event_list = {"queryStringParameters": {"student_id": "ghost"}}
    resp = list_submissions.handler(event_list, {})
    data = json.loads(resp["body"])
    assert data["total"] == 0
    assert data["items"] == []
