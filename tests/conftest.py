import pytest
import time
import requests

BASE_URL = "http://localhost:5001/api"


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def auth_token():
    """Registers a user and returns the auth token."""
    # Create unique username using timestamp
    timestamp = int(time.time() * 1000)
    username = f"testuser{timestamp}"

    # Register user
    user_data = {
      "username": username,
      "password": "securepassword123"
    }
    requests.post(f"{BASE_URL}/auth/register", json=user_data)

    # Login user
    response = requests.post(f"{BASE_URL}/auth/login", json=user_data)
    return response.json()['access_token']