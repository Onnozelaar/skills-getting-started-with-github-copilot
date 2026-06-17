import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_state))


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert isinstance(data[expected_activity]["participants"], list)


def test_signup_adds_new_participant_successfully():
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"

    activity_response = client.get("/activities").json()[activity_name]
    assert new_email in activity_response["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_successfully():
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": existing_email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {existing_email} from {activity_name}"

    activity_response = client.get("/activities").json()[activity_name]
    assert existing_email not in activity_response["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missingstudent@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": missing_email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_participant_from_missing_activity_returns_404():
    # Arrange
    missing_activity = "Nonexistent Club"
    email = "someone@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{missing_activity}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
