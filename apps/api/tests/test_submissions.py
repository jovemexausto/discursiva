import pytest
from httpx import ASGITransport, AsyncClient

from discursiva_domain.use_cases import GetSubmission, ListSubmissions, SubmitAnswer
from tests.fakes import FakeQueue, FakeStorage, FakeSubmissionRepository  # type: ignore

from api.main import app
from api import dependencies


@pytest.fixture
def fakes():
    return FakeSubmissionRepository(), FakeStorage(), FakeQueue()


@pytest.fixture
async def client(fakes):
    repo, storage, queue = fakes

    async def _submit(): return SubmitAnswer(repo=repo, storage=storage, queue=queue)
    async def _get():    return GetSubmission(repo=repo)
    async def _list():   return ListSubmissions(repo=repo)

    app.dependency_overrides[dependencies.get_submit_answer]    = _submit
    app.dependency_overrides[dependencies.get_get_submission]   = _get
    app.dependency_overrides[dependencies.get_list_submissions] = _list

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()



async def test_create_returns_201(client):
    resp = await client.post("/submissions", json={"student_id": "s1", "text": "texto"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["student_id"] == "s1"
    assert data["status"] == "PENDING"
    assert data["score"] is None
    assert "id" in data


async def test_create_missing_text_returns_422(client):
    resp = await client.post("/submissions", json={"student_id": "s1"})
    assert resp.status_code == 422


async def test_create_empty_student_id_returns_422(client):
    resp = await client.post("/submissions", json={"student_id": "", "text": "texto"})
    assert resp.status_code == 422



async def test_get_existing_submission(client):
    create = await client.post("/submissions", json={"student_id": "s1", "text": "t"})
    sid = create.json()["id"]
    resp = await client.get(f"/submissions/{sid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == sid


async def test_get_nonexistent_returns_404(client):
    import uuid
    resp = await client.get(f"/submissions/{uuid.uuid4()}")
    assert resp.status_code == 404


async def test_get_invalid_id_returns_404(client):
    resp = await client.get("/submissions/not-a-uuid")
    assert resp.status_code == 404



async def test_list_returns_all_for_student(client):
    for i in range(3):
        await client.post("/submissions", json={"student_id": "s2", "text": f"t{i}"})
    resp = await client.get("/submissions", params={"student_id": "s2"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


async def test_list_pagination(client):
    for i in range(5):
        await client.post("/submissions", json={"student_id": "s3", "text": f"t{i}"})
    resp = await client.get("/submissions", params={"student_id": "s3", "limit": 2, "offset": 0})
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2


async def test_list_missing_student_id_returns_422(client):
    resp = await client.get("/submissions")
    assert resp.status_code == 422


async def test_list_empty_student_returns_empty_page(client):
    resp = await client.get("/submissions", params={"student_id": "ghost"})
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []



async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
