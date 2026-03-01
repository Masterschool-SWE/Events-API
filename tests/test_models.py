from models import User


def test_user_password_hashing_behaves_correctly():
    """Test that password checking and hashing works correctly"""

    # arrange: Create a user

    user = User(username="aline")
    user.set_password("mypassword123")

    # act and assert
    assert user.check_password("mypassword123") is True
    assert user.check_password("wrongpassword") is False
    assert user.password_hash != "mypassword123"
    assert user.password_hash is not None
