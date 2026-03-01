import requests
import time


def test_health_endpoint_returns_healthy(base_url):
    """Test health endpoint"""
    # act
    response = requests.get(f"{base_url}/health")

    # assert
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"


def test_register_user_creates_new_user(base_url):
    """Test registering a new user"""
    timestamp = int(time.time() * 1000)
    response = requests.post(
        f"{base_url}/auth/register",
        json={
            "username": f"testuser{timestamp}",
            "password": "securepassword123"
        }
    )

    assert response.status_code == 201
    body = response.json()
    assert "user" in body
    user_data = body["user"]
    assert user_data["username"] == f"testuser{timestamp}"


def test_login_returns_jwt_token(base_url):
    """Test logging in and getting JWT token"""
    timestamp = int(time.time() * 1000)
    username = f"testuser{timestamp}"
    password = "securepassword123"

    # register first
    requests.post(
        f"{base_url}/auth/register",
        json={
            "username": username,
            "password": password
        }
    )

    # then login
    response = requests.post(
        f"{base_url}/auth/login",
        json={
            "username": username,
            "password": password
        }
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["access_token"] != ""


def test_create_public_event_requires_auth_and_succeeds_with_token(base_url, auth_token):
    """Test creating an event"""
    # arrange: event data
    event_data = {
      "title": "New event test",
      "description": "This is a test event",
      "date": "2026-01-20T18:00:00",
      "location": "Tech Hub, Room 20",
      "capacity": 50,
      "is_public": True,
      "requires_admin": False
    }

    # act
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.post(f"{base_url}/events",
                             json=event_data,
                             headers=headers)

    # assert
    assert response.status_code == 201

    body = response.json()

    assert body["title"] == event_data["title"]
    assert body["description"] == event_data["description"]
    assert body["location"] == event_data["location"]
    assert body["capacity"] == event_data["capacity"]
    assert body["is_public"] is True


def test_rsvp_to_public_event(base_url, auth_token):
    """Test registration for a public event"""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create event
    event_data = {
        "title": "RSVP Event",
        "description": "Event for RSVP test",
        "date": "2026-01-20T18:00:00",
        "location": "Conference Hall",
        "capacity": 100,
        "is_public": True,
        "requires_admin": False
    }

    event_response = requests.post(
        f"{base_url}/events",
        json=event_data,
        headers=headers
    )

    assert event_response.status_code == 201
    event_id = event_response.json()["id"]

    # RSVP
    rsvp_response = requests.post(
        f"{base_url}/rsvps/event/{event_id}",
        json={},
        headers=headers
    )

    assert rsvp_response.status_code == 201

    body = rsvp_response.json()
    assert body["event_id"] == event_id


def test_login_fails_with_wrong_password(base_url):
    timestamp = int(time.time() * 1000)
    username = f"user{timestamp}"
    password = "correctpassword"

    # register
    requests.post(
        f"{base_url}/auth/register",
        json={"username": username, "password": password}
    )

    # login with wrong password
    response = requests.post(
        f"{base_url}/auth/login",
        json={"username": username, "password": "wrongpassword"}
    )

    assert response.status_code == 401


def test_create_event_fails_without_auth(base_url):
    event_data = {
        "title": "Unauthorized Event",
        "description": "Should fail",
        "date": "2026-01-20T18:00:00",
        "location": "Nowhere",
        "capacity": 10,
        "is_public": True,
        "requires_admin": False
    }

    response = requests.post(
        f"{base_url}/events",
        json=event_data
    )

    assert response.status_code == 401


def test_rsvp_fails_without_auth(base_url, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create event first
    event_data = {
        "title": "Public Event",
        "description": "Test",
        "date": "2026-01-20T18:00:00",
        "location": "Room 1",
        "capacity": 50,
        "is_public": False,
        "requires_admin": False
    }

    event_response = requests.post(
        f"{base_url}/events",
        json=event_data,
        headers=headers
    )

    event_id = event_response.json()["id"]

    # Try RSVP without token
    response = requests.post(
        f"{base_url}/rsvps/event/{event_id}",
        json={}
    )

    assert response.status_code == 401


