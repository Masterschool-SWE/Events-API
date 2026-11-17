import pytest

from models import db, User, Event
from app import create_app, db


@pytest.fixture
def app():
    """Erstellt eine Flask-App-Instanz für die Tests."""
    # Wir erstellen die App im Testmodus und nutzen z.B. eine SQLite In-Memory-DB
    app = create_app()

    with app.app_context():
        db.create_all()  # Tabellen für die Tests anlegen
        yield app  # Hier läuft der eigentliche Test
        db.drop_all()  # Danach alles wieder aufräumen

@pytest.fixture
def test_user():
    user = User(username="test")
    user.set_password("mysecretpassword")
    return user

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

def test_get_single_event(app):
    """get single event by id"""
    # Wir gehen davon aus, dass es immer ein erstes Event gibt
    event_id = 1
    event = Event.query.get(event_id)

    assert isinstance(event, Event)

def test_get_single_event_false(app):
    """get no event by invalid, too big id"""
    event_id = 19999999999999999
    event = Event.query.get(event_id)

    assert event is None
