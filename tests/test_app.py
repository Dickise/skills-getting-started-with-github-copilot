from fastapi.testclient import TestClient
import pytest

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a deep-ish copy of initial activities so tests can modify global state
    original = {
        name: {
            "description": details["description"],
            "schedule": details["schedule"],
            "max_participants": details["max_participants"],
            "participants": list(details["participants"]),
        }
        for name, details in app_module.activities.items()
    }
    yield
    # restore
    app_module.activities.clear()
    app_module.activities.update(original)


def test_get_activities():
    client = TestClient(app_module.app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_duplicate_signup():
    client = TestClient(app_module.app)
    email = "test_student@mergington.edu"
    activity = "Chess Club"

    # Ensure student not present
    assert email not in app_module.activities[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # Duplicate signup should fail
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400


def test_unregister():
    client = TestClient(app_module.app)
    activity = "Programming Class"
    email = "temp_student@mergington.edu"

    # Add temp student
    app_module.activities[activity]["participants"].append(email)
    assert email in app_module.activities[activity]["participants"]

    # Unregister
    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    assert email not in app_module.activities[activity]["participants"]

    # Unregistering someone not registered should return 400
    resp2 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp2.status_code == 400
