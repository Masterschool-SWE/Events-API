import requests

def test_health_endpoint_returns_healthy(base_url):
    # Send a GET request to the health endpoint
    response = requests.get(f"{base_url}/api/health", timeout=5)

    # Check that the status code is 200
    assert response.status_code == 200

    # Check that the API reports a healthy status
    assert response.json()["status"] == "healthy"


def test_user_registration(base_url, registration_user):
    # Arrange
    data = registration_user

    # Act
    response = requests.post(
        f"{base_url}/api/auth/register",
        json=data,
        timeout=5
    )

    # Assert
    assert response.status_code == 201
    assert response.json()["message"] == "User created successfully"
    assert response.json()["user"]["username"] == data["username"]

def test_user_login(base_url, registered_user):
    # Arrange
    data = registered_user

    # Act: Log in with the registered user
    response = requests.post(
        f"{base_url}/api/auth/login",
        json=data,
        timeout=5
    )

    # Assert: Check successful login
    assert response.status_code == 200

    # Check that an access token was returned
    assert "access_token" in response.json()
    assert isinstance(response.json()["access_token"], str)
    assert response.json()["access_token"]

    # Check that the correct user is logged in
    assert response.json()["user"]["username"] == data["username"]


def test_create_event(base_url, auth_token, event_data):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    # Act:
    response = requests.post(
        f"{base_url}/api/events",
        json=event_data,
        headers=headers,
        timeout=5
    )

    # Assert: Check successful login
    assert response.status_code == 201, (
        f"Event creation failed!\n"
        f"Expected status: 201 (Created)\n"
        f"Actual status: {response.status_code}\n"
        f"API response: {response.text}"
    )
    # Check that the event title, description, location matches the submitted title, description, location
    assert response.json()["title"] == event_data["title"]
    assert response.json()["description"] == event_data["description"]
    assert response.json()["location"] == event_data["location"]

def test_rsvp_event(base_url, auth_token, event_data):
    # Arrange: Prepare authentication
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    event_response = requests.post(
        f"{base_url}/api/events",
        json=event_data,
        headers=headers,
        timeout=5
    )

    # Get the ID of the created event
    event_id = event_response.json()["id"]

    # Create RSVP to the created event
    response = requests.post(
        f"{base_url}/api/rsvps/event/{event_id}",
        json={"attending": True},
        headers=headers,
        timeout=5
    )

    # Assert: Check successful RSVP creation
    assert response.status_code == 201, (
        f"RSVP creation failed!\n"
        f"Expected status: 201 (Created)\n"
        f"Actual status: {response.status_code}\n"
        f"API response: {response.text}"
    )

    # Check that the RSVP belongs to the correct event
    assert response.json()["event_id"] == event_id

    # Check that the user is attending the event
    assert response.json()["attending"] is True


def test_duplicate_registration(base_url, registered_user):
    # Arrange: Use the credentials of an already registered user
    data = registered_user
    expected_status = 400

    # Act: Try to register the same user again
    response = requests.post(
        f"{base_url}/api/auth/register",
        json=data,
        timeout=5
    )

    # Assert: Check that duplicate registration is rejected
    assert response.status_code == expected_status, (
        f"Duplicate registration test failed!\n"
        f"Expected status: {expected_status}\n"
        f"Actual status: {response.status_code}\n"
        f"API response: {response.text}"
    )

    # Check that the API returns the correct error message
    assert response.json()["error"] == "Username already exists"

def test_create_event_without_authentication(base_url, event_data):
    # Arrange: Set the expected HTTP status
    expected_status = 401

    # Act: Try to create an event without authentication
    response = requests.post(
        f"{base_url}/api/events",
        json=event_data,
        timeout=5
    )

    # Assert: Check that the request is rejected
    assert response.status_code == expected_status, (
        f"Unauthorized event creation test failed!\n"
        f"Expected status: {expected_status}\n"
        f"Actual status: {response.status_code}\n"
        f"API response: {response.text}"
    )

    # Check the API error message
    assert response.json()["msg"] == "Missing Authorization Header"


def test_private_rsvp_without_authentication(base_url, auth_token, event_data):
    # Arrange: Set the expected HTTP status
    expected_status = 401

    # Prepare private event data
    private_event_data = event_data.copy()
    private_event_data["is_public"] = False

    # Create a private event with authentication
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    event_response = requests.post(
        f"{base_url}/api/events",
        json=private_event_data,
        headers=headers,
        timeout=5
    )

    # Verify that the private event was created
    assert event_response.status_code == 201, event_response.text

    event_id = event_response.json()["id"]

    # Act: Try to RSVP without authentication
    response = requests.post(
        f"{base_url}/api/rsvps/event/{event_id}",
        json={"attending": True},
        timeout=5
    )

    # Assert: Check that unauthorized RSVP is rejected
    assert response.status_code == expected_status, (
        f"Unauthorized private RSVP test failed!\n"
        f"Expected status: {expected_status}\n"
        f"Actual status: {response.status_code}\n"
        f"API response: {response.text}"
    )

    # Verify the error message
    assert response.json()["error"] == "Authentication required for this event"