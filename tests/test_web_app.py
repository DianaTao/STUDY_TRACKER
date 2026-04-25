import pytest
from pathlib import Path
from src.web_app import app, store

@pytest.fixture
def client(tmp_path):
    app.config["TESTING"] = True
    test_db = tmp_path / "test_sessions.json"
    store.storage_path = test_db
    store._save_data([]) # Reset
    with app.test_client() as client:
        yield client

def test_dashboard_status_code(client):
    """The dashboard should be accessible via GET."""
    response = client.get("/")
    assert response.status_code == 200

def test_add_session_creates_record(client):
    """POSTing a valid session should redirect and persist data."""
    data = {"topic": "Math", "minutes": "30", "mood": "Happy", "notes": "Algebra"}
    response = client.post("/sessions/add", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Math" in response.data

def test_add_session_invalid_data(client):
    """POSTing negative minutes should return an error."""
    data = {"topic": "Math", "minutes": "-5", "mood": "Sad", "notes": ""}
    response = client.post("/sessions/add", data=data)
    assert response.status_code == 400
    assert b"Minutes must be positive" in response.data

def test_demo_reset_seeds_data(client):
    """The demo-reset endpoint should populate the store with initial data."""
    client.post("/demo-reset", follow_redirects=True)
    response = client.get("/sessions")
    assert b"Python" in response.data
    assert b"Flask" in response.data