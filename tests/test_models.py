from datetime import datetime

import pytest

from models import db, User, Event
from app import create_app, db

TEST_EVENT = {
    "title": "Test Event",
    "description": "Test Description",
    "date": "2026-01-15T18:00:00",
    "location": "Test Room",
    "capacity": 50,
    "is_public": False,
    "requires_admin": False
}

@pytest.fixture
def app():
    """Erstellt eine Flask-App-Instanz für die Tests."""
    # Wir erstellen die App im Testmodus und nutzen z.B. eine SQLite In-Memory-DB
    app = create_app()

    with app.app_context():
        yield app  # Hier läuft der eigentliche Test

@pytest.fixture
def test_user():
    user = User(username="test")
    user.set_password("mysecretpassword")
    return user

@pytest.fixture(autouse=True)
def event_to_test(app):
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
        event = db.session.get(Event, event_id)
        if event:
            db.session.delete(event)
            db.session.commit()

def test_user_password_hashing(test_user):
    """test the password hashing"""
    # Arrange: Create User
    user = test_user

    # Act & Assert: Check correct password
    assert user.check_password(password="mysecretpassword") == True

    # Act & Assert: Check wrong password
    assert user.check_password(password="mysecretpassword_xxx") == False

    # Act & Assert: Password is stored
    assert user.password_hash is not None

    # Act & Assert: Stored password is nit plain password
    assert user.password_hash != "mysecretpassword"

def test_get_single_event(app, event_to_test):
    """get single event by id"""
    with app.app_context():

        event_id = event_to_test
        event = db.session.get(Event, event_id)

        assert isinstance(event, Event)

def test_get_single_event_false(app):
    """get no event by invalid, too big id"""
    with app.app_context():

        event_id = 19999999999999999
        event = db.session.get(Event, event_id)

#        assert event is None
        assert event is 3
