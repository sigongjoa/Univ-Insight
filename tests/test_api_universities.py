
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_list_universities():
    """
    UC-002: Verify that the /universities endpoint returns a list of universities.
    """
    response = client.get("/api/v1/universities")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total_count" in data
    assert data["total_count"] > 0
    
    # Check if Seoul National University is present
    snu = next((u for u in data["items"] if u["name"] == "Seoul National University"), None)
    assert snu is not None
    assert snu["name_ko"] == "서울대학교"

def test_get_university_detail():
    """
    UC-003: Verify that /universities/{id} returns detailed information.
    """
    # First get the ID from the list
    response = client.get("/api/v1/universities")
    data = response.json()
    snu = next((u for u in data["items"] if u["name"] == "Seoul National University"), None)
    assert snu is not None
    uni_id = snu["id"]
    
    # Get detail
    response = client.get(f"/api/v1/universities/{uni_id}")
    assert response.status_code == 200
    detail = response.json()
    assert detail["id"] == uni_id
    assert detail["name"] == "Seoul National University"
    assert "colleges" in detail

def test_trigger_crawl():
    """
    UC-004: Verify that /admin/crawl triggers a job.
    """
    # Use a dummy ID that we know exists (from previous tests)
    # We need to fetch it first to be sure
    response = client.get("/api/v1/universities")
    data = response.json()
    if not data["items"]:
        pytest.skip("No universities found")
        
    uni_id = data["items"][0]["id"]
    
    payload = {
        "university_id": uni_id,
        "target_url": "https://example.com"
    }
    
    response = client.post("/api/v1/admin/crawl", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "queued"
    assert result["university_id"] == uni_id
