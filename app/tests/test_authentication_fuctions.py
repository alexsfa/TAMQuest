import pytest
from unittest.mock import MagicMock, patch
import services.authentication_functions as auth_funcs

def test_login_user_success():
    supabase_client = MagicMock()
    expected_user = {"user": {"id": "user_123"}}

    supabase_client.auth.sign_in_with_password.return_value = expected_user

    result = auth_funcs.login_user(
        supabase_client,
        email="test@example.com",
        password="password123"
    )

    assert result == expected_user
    supabase_client.auth.sign_in_with_password.assert_called_once_with({
        "email": "test@example.com",
        "password": "password123"
    })

@patch("services.authentication_functions.st.error")
def test_login_user_failure(mock_st_error):
    supabase_client = MagicMock()
    supabase_client.auth.sign_in_with_password.side_effect = Exception("Invalid credentials")

    result = auth_funcs.login_user(
        supabase_client,
        email="test@example.com",
        password="wrongpassword"
    )

    assert result is None
    mock_st_error.assert_called_once()
    assert "Log in has failed" in mock_st_error.call_args[0][0]

@patch("services.authentication_functions.st.success")
def test_signup_user_success(mock_st_success):
    supabase_client = MagicMock()

    auth_funcs.signup_user(
        supabase_client,
        email="test@example.com",
        password="password123"
    )

    supabase_client.auth.sign_up.assert_called_once_with({
        "email": "test@example.com",
        "password": "password123",
        "options": {
            "data": {
                "role": "user"
            }
        }
    })
    
    mock_st_success.assert_called_once_with(
        "Signed up successfully. Please check your email for confirmation."
    )

@patch("services.authentication_functions.st.error")
def test_signup_user_failure(mock_st_error):
    supabase_client = MagicMock()
    supabase_client.auth.sign_up.side_effect = Exception("Email already exists")

    auth_funcs.signup_user(
        supabase_client,
        email="test@example.com",
        password="password123"
    )

    mock_st_error.assert_called_once()
    assert "Sign up has failed" in mock_st_error.call_args[0][0]

    