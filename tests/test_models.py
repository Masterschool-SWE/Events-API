import pytest

from models import User

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
