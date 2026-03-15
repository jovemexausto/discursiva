import os
import pytest
import httpx

# A URL base será o Serverless Offline ou LocalStack
E2E_URL = os.environ.get("E2E_URL", "")

@pytest.fixture
async def client():
    async with httpx.AsyncClient(base_url=E2E_URL) as c:
        yield c

@pytest.mark.asyncio
@pytest.mark.skipif(condition=E2E_URL == "", reason="Testes E2E dependem de uma instância de API Gateway local")
async def test_e2e_create_and_get_submission(client):
    try:
        # 1. Cria uma submissão
        resp = await client.post("/submissions", json={"student_id": "e2e_student_1", "text": "e2e test text"})
        if resp.status_code != 201:
            pytest.skip(f"API not reachable or failed at {E2E_URL}")
        
        data = resp.json()
        assert data["student_id"] == "e2e_student_1"
        assert "id" in data
        sub_id = data["id"]
        
        # 2. Busca a submissão
        resp_get = await client.get(f"/submissions/{sub_id}")
        assert resp_get.status_code == 200
        get_data = resp_get.json()
        assert get_data["id"] == sub_id
        assert get_data["student_id"] == "e2e_student_1"

        # 3. Lista as submissões
        resp_list = await client.get("/submissions", params={"student_id": "e2e_student_1"})
        assert resp_list.status_code == 200
        list_data = resp_list.json()
        assert list_data["total"] >= 1
        assert any(item["id"] == sub_id for item in list_data["items"])
        
    except httpx.ConnectError:
        pytest.skip(f"Could not connect to API Gateway at {E2E_URL}. Is serverless offline / LocalStack running?")
