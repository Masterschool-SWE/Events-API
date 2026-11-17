from datetime import datetime

import pytest
import requests
from werkzeug.security import generate_password_hash

from app import create_app
from models import db, User, Event

app = create_app()
BASE_URL = 'http://127.0.0.1:5000'

NEW_USER = {
    'username': 'new_user',
    'password': 'new_password',
}
TEST_USER = {
    'username': 'test_user',
    'password': 'test_password',
}
NEW_EVENT = {
    "title": "New Event",
    "description": "New Description",
    "date": "2026-01-15T18:00:00",
    "location": "New Room",
    "capacity": 50,
    "is_public": True,
    "requires_admin": False
}
TEST_EVENT = {
    "title": "Test Event",
    "description": "Test Description",
    "date": "2026-01-15T18:00:00",
    "location": "Test Room",
    "capacity": 50,
    "is_public": False,
    "requires_admin": False
}

@pytest.fixture(autouse=True)
def user_to_test():
    """
    create test data for user and event
    clear database after testing is done
    """
    with app.app_context():

        # All about TEST_USER
        existing = User.query.filter_by(username=TEST_USER['username']).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()

        # Neuen User erstellen
        user = User(username=TEST_USER['username'], password_hash=generate_password_hash(TEST_USER['password']))
        db.session.add(user)
        db.session.commit()

        yield

        # Cleanup database: New User
        user = User.query.filter_by(username=NEW_USER['username']).first()
        if user:
            db.session.delete(user)
            db.session.commit()

@pytest.fixture(autouse=True)
def event_to_test():
    """
    create test data for event
    clear database after testing is done
    """
    with app.app_context():

        # All about Test Event
        event_date = datetime.fromisoformat(str(TEST_EVENT["date"]).replace('Z', '+00:00'))
        event = Event(
            title=TEST_EVENT["title"],
            description=TEST_EVENT["description"],
            date=event_date,
            location=TEST_EVENT["location"],
            capacity=TEST_EVENT["capacity"],
            is_public=TEST_EVENT["is_public"],
            requires_admin=TEST_EVENT["requires_admin"]
        )
        db.session.add(event)
        db.session.commit()

        # Wir speichern uns die ID, damit wir das Event nach dem Test genau wiederfinden
        event_id = event.id

        yield event.id

        # Cleanup database: Test Event
        event = Event.query.get(event_id)
        if event:
            db.session.delete(event)
            db.session.commit()


def test_health_check():
    """test the health check endpoint"""
    # Arrange

    # Act
    response = requests.get(f"{BASE_URL}/api/health")

    # Assert
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'


def test_register_user():
    # Arrange

    #Act
    response = requests.post(f"{BASE_URL}/api/auth/register", json=NEW_USER)

    # Assert
    assert response.status_code == 201

def test_login_user():
    # Arrange

    #Act
    response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)

    # Assert
    assert response.status_code == 200

def test_create_event():
    # Arrange
    # get token
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
    token = login_response.json().get('access_token') or login_response.json().get('token')
    headers = {
        'Authorization': f'Bearer {token}'
    }
    #Act
    response = requests.post(f"{BASE_URL}/api/events", json=NEW_EVENT, headers=headers)

    # Assert
    assert response.status_code == 201

def test_rsvp_event(event_to_test):
    # Arrange
    event_id = event_to_test

    # get token
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
    token = login_response.json().get('access_token') or login_response.json().get('token')
    headers = {
        'Authorization': f'Bearer {token}'
    }

    rsvp_json = {
      "attending": True
    }
    #Act
    response = requests.post(f"{BASE_URL}/api/rsvps/event/{event_id}", json=rsvp_json, headers=headers)

    # Assert
    assert response.status_code == 201


def test_register_duplicate_username_fails():
    # Arrange

    #Act
    # create user the first time: ok
    requests.post(f"{BASE_URL}/api/auth/register", json=NEW_USER)
    # create user the second time: error
    response = requests.post(f"{BASE_URL}/api/auth/register", json=NEW_USER)

    # Assert
    assert response.status_code == 400

def test_create_event_unauthenticated_fails():
    # Arrange

    #Act
    response = requests.post(f"{BASE_URL}/api/events", json=NEW_EVENT)

    # Assert
    assert response.status_code == 401

def test_rsvp_private_event_unauthenticated_fails(event_to_test):
    # Arrange
    event_id = event_to_test

    rsvp_json = {
      "attending": True
    }
    #Act
    response = requests.post(f"{BASE_URL}/api/rsvps/event/{event_id}", json=rsvp_json)

    # Assert
    assert response.status_code == 401
