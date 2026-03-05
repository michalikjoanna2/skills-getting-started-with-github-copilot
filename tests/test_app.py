from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Arrange: keep a pristine copy of the activities and restore after each test."""
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_root_redirect():
    # Arrange is handled by fixture
    # Act
    response = client.get("/")
    # Assert
    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_success():
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert "Signed up" in response.json()["message"]


def test_signup_duplicate():
    email = "daniel@mergington.edu"  # already in Chess Club
    activity_name = "Chess Club"
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_not_found():
    email = "ghost@mergington.edu"
    activity_name = "Nonexistent Club"
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_success():
    email = "michael@mergington.edu"
    activity_name = "Chess Club"
    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert "Unregistered" in response.json()["message"]


def test_unregister_not_signed():
    email = "nobody@mergington.edu"
    activity_name = "Chess Club"
    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"


def test_unregister_not_found():
    email = "ghost@mergington.edu"
    activity_name = "Nonexistent Club"
    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"