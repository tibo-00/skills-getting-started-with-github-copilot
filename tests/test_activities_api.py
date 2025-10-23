from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # make a deep-ish copy of activities to restore after each test
    original = {k: {**v, "participants": list(v.get("participants", []))} for k, v in activities.items()}
    yield
    activities.clear()
    activities.update({k: {**v, "participants": list(v.get("participants", []))} for k, v in original.items()})


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "teststudent@mergington.edu"

    # Ensure email not already in participants
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]

    # Confirm added
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json()["message"]

    # Confirm removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]


def test_unregister_not_registered():
    activity = "Programming Class"
    email = "nobody@mergington.edu"

    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student not registered for this activity"


def test_signup_activity_not_found():
    resp = client.post("/activities/Nonexistent/signup?email=a@b.com")
    assert resp.status_code == 404


def test_unregister_activity_not_found():
    resp = client.delete("/activities/Nonexistent/unregister?email=a@b.com")
    assert resp.status_code == 404
