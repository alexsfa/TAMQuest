import pytest
from unittest.mock import MagicMock
from database.profiles import Profiles

@pytest.fixture
def mock_supabase_client():
    client = MagicMock()
    table = MagicMock()
    query = MagicMock()

    client.table.return_value = table
    table.select.return_value = query
    table.insert.return_value = query
    table.update.return_value = query
    table.delete.return_value = query

    query.eq.return_value = query
    query.neq.return_value = query

    query.execute.return_value = {"data": "mocked_result"}

    return client

def test_get_all_profiles(mock_supabase_client):
    profiles = Profiles(mock_supabase_client)

    result = profiles.get_all_profiles("user-123")

    mock_supabase_client.table.assert_called_once_with("profiles")
    mock_supabase_client.table().select.assert_called_once()
    mock_supabase_client.table().select().neq.assert_any_call("id", "user-123")
    mock_supabase_client.table().select().execute.assert_called_once()

    assert result == {"data": "mocked_result"}

def test_get_profile_by_id(mock_supabase_client):
    profiles = Profiles(mock_supabase_client)

    result = profiles.get_profile_by_id("user-123")

    mock_supabase_client.table.assert_called_once_with("profiles")
    mock_supabase_client.table().select.assert_called_once()
    mock_supabase_client.table().select().eq.assert_any_call("id", "user-123")
    mock_supabase_client.table().select().execute.assert_called_once()

    assert result == {"data": "mocked_result"}

def test_create_profile(mock_supabase_client):
    profiles = Profiles(mock_supabase_client)

    result = profiles.create_profile("user-123", "test_user", "1900-01-01", "test_city", "test_country")
    
    mock_supabase_client.table.assert_called_once_with("profiles")
    mock_supabase_client.table().insert.assert_called_once_with({
        "id": "user-123", 
        "full_name": "test_user",
        "birthdate": "1900-01-01",
        "city": "test_city", 
        "country": "test_country",
    })
    mock_supabase_client.table().insert().execute.assert_called_once()

    assert result == {"data": "mocked_result"}

def test_update_profile_by_id(mock_supabase_client):
    profiles = Profiles(mock_supabase_client)

    result = profiles.update_profile_by_id("user-123", None, "2025-01-01", None, "updated_test_country",
    "old_test_user", "1900-01-01", "old_test_city", "old_test_country")

    mock_supabase_client.table.assert_called_once_with("profiles")
    mock_supabase_client.table().update.assert_called_once_with({
        "id": "user-123",
        "full_name": "old_test_user",
        "birthdate": "2025-01-01",  # fallback to old
        "city": "old_test_city",
        "country": "updated_test_country"    # fallback to old
    })
    mock_supabase_client.table().update().eq.assert_called_once_with("id", "user-123")
    mock_supabase_client.table().update().execute.assert_called_once()

    assert result == {"data": "mocked_result"}

def test_delete_profile_by_id(mock_supabase_client):
    profiles = Profiles(mock_supabase_client)

    result = profiles.delete_profile_by_id("user-123")

    mock_supabase_client.table.assert_called_once_with("profiles")
    mock_supabase_client.table().delete.assert_called_once()
    mock_supabase_client.table().delete().eq.assert_any_call("id", "user-123")
    mock_supabase_client.table().delete().execute.assert_called_once()

    assert result == {"data": "mocked_result"}

def test_get_all_profiles_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    profiles = Profiles(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to retrieve profiles"):
        profiles.get_all_profiles("user-123")

def test_get_profile_by_id_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    profiles = Profiles(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to retrieve profile"):
        profiles.get_profile_by_id("user-123")

def test_create_profile_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    profiles = Profiles(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to create profile"):
        profiles.create_profile("user-123", "test_name", "1900-01-01", "test_city", "test_country")

def test_update_profile_by_id_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    profiles = Profiles(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to update profile"):
        profiles.update_profile_by_id("user-123", "new_test_name", "2025-01-01", "new_test_city", "new_test_country",
        "old_test_name", "1900-01-01", "old_test_city", "old_test_country")

def test_delete_profile_by_id_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    profiles = Profiles(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to delete profile"):
        profiles.delete_profile_by_id("user-123")



