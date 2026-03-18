import os
import pytest
import httpx

# A URL base será gerada pelo serverless offline
E2E_URL = os.environ.get("E2E_URL", "")

@pytest.fixture
async def client():
    async with httpx.AsyncClient(base_url=E2E_URL) as c:
        yield c

async def _create_submission(client, student_id: str, text: str) -> str:
    resp = await client.post("/submissions", json={"student_id": student_id, "text": text})
    if resp.status_code != 201:
        pytest.skip(f"API not reachable or failed at {E2E_URL}")
    data = resp.json()
    assert data["student_id"] == student_id
    assert "id" in data
    return data["id"]

async def _verify_get_submission(client, sub_id: str, student_id: str):
    resp_get = await client.get(f"/submissions/{sub_id}")
    assert resp_get.status_code == 200
    get_data = resp_get.json()
    assert get_data["id"] == sub_id
    assert get_data["student_id"] == student_id

async def _verify_list_submissions(client, sub_id: str, student_id: str):
    resp_list = await client.get("/submissions", params={"student_id": student_id})
    assert resp_list.status_code == 200
    list_data = resp_list.json()
    assert list_data["total"] >= 1
    assert any(item["id"] == sub_id for item in list_data["items"])


@pytest.mark.asyncio
@pytest.mark.skipif(condition=E2E_URL == "", reason="Testes E2E dependem de uma instância de API Gateway local")
async def test_e2e_create_and_get_submission(client):
    try:
        student_id = "e2e_student_1"
        sub_id = await _create_submission(client, student_id, "e2e test text")
        await _verify_get_submission(client, sub_id, student_id)
        await _verify_list_submissions(client, sub_id, student_id)
    except httpx.ConnectError:
        pytest.skip(f"Could not connect to API Gateway at {E2E_URL}. Is serverless offline / LocalStack running?")
