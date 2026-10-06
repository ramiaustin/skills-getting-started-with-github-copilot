from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities_state():
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_activity_data():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert expected_activity in payload
    assert "participants" in payload[expected_activity]
    assert "schedule" in payload[expected_activity]


def test_signup_for_activity_success():
    # Arrange
    activity_name = "Basketball Team"
    email = "newstudent@mergington.edu"
    before_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email.lower()} for {activity_name}"
    assert email.lower() in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == before_count + 1


def test_signup_for_activity_rejects_duplicate_signups():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_for_activity_rejects_unknown_activity():
    # Arrange
    activity_name = "Not Real Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_activity_rejects_when_full():
    # Arrange
    activity_name = "Basketball Team"
    max_participants = activities[activity_name]["max_participants"]
    activities[activity_name]["participants"] = [
        f"student{i}@mergington.edu" for i in range(max_participants)
    ]
    email = "overflow@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"
