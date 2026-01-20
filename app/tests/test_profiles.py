import pytest
from unittest.mock import MagicMock
from database.profiles import Profiles


class MockSupabaseResponse:
    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error

@pytest.fixture
def supabase_client():
    client = MagicMock()

    query = MagicMock()
    query.eq.return_value = query
    query.neq.return_value = query
    query.order.return_value = query

    client.table.return_value.select.return_value = query
    client.table.return_value.insert.return_value = query
    client.table.return_value.update.return_value = query
    client.table.return_value.delete.return_value = query

    return client

def test_get_all_profiles(supabase_client):
    expected_data = [
        {   
            "id": "user_1",
            "full_name": "alex",
            "birthdate": "2001-01-28",
            "created_at": "2026-01-05 23:23:34.773619+00",
            "updated_at": "2026-01-05 23:23:34.773619+00",
            "city": "Nikaia",
            "country": "Greece"
        }
    ]

    supabase_client.table.return_value \
        .select.return_value \
        .neq.return_value \
        .execute.return_value = MockSupabaseResponse(data=expected_data)

    profiles = Profiles(supabase_client)

    result = profiles.get_all_profiles("admin_123")

    assert result.data == expected_data

def test_get_profile_by_id(supabase_client):
    expected_data = [
        {   
            "id": "user_1",
            "full_name": "alex",
            "birthdate": "2001-01-28",
            "created_at": "2026-01-05 23:23:34.773619+00",
            "updated_at": "2026-01-05 23:23:34.773619+00",
            "city": "Nikaia",
            "country": "Greece"
        }
    ]

    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .execute.return_value = MockSupabaseResponse(data=expected_data)

    profiles = Profiles(supabase_client)

    result = profiles.get_profile_by_id("user_1")

    assert result.data == expected_data

def test_create_profile(supabase_client):
    inserted_data = [
        {
            "id": "user_123",
            "full_name": "alex",
            "birthdate": "2001-01-28",
            "city": "Nikaia",
            "country": "Greece"
        }
    ]

    supabase_client.table.return_value \
        .insert.return_value \
        .execute.return_value = MockSupabaseResponse(data=inserted_data)

    profiles = Profiles(supabase_client)

    result = profiles.create_profile("user_123", "alex", "2001-01-28", "Nikaia", "Greece")

    assert result.data == inserted_data


def test_update_profile_by_id(supabase_client):
    old_profile = {
        "full_name": "Old Name",
        "birthdate": "1990-01-01",
        "city": "Old City",
        "country": "Old Country",
    }
    new_values = {
        "full_name": "New Name",
        "birthdate": "1991-02-02",
        "city": "New City",
        "country": "New Country",
    }

    updated_data = [
        {
            "id": "user_123",
            **new_values
        }
    ]

    supabase_client.table.return_value.update.return_value \
        .eq.return_value \
        .execute.return_value = MockSupabaseResponse(data=updated_data)

    profiles = Profiles(supabase_client)

    result = profiles.update_profile_by_id(
        "user_123",
        new_values["full_name"],
        new_values["birthdate"],
        new_values["city"],
        new_values["country"],
        old_profile["full_name"],
        old_profile["birthdate"],
        old_profile["city"],
        old_profile["country"],
    )

    assert result.data == updated_data

def test_update_profile_by_id_uses_old_value_if_new_missing(supabase_client):

    old_profile = {
        "full_name": "Old Name",
        "birthdate": "1990-01-01",
        "city": "Old City",
        "country": "Old Country",
    }

    updated_data = [
        {
            "id": "user_123",
            "full_name": "Old Name",   # new_full_name is None → old value used
            "birthdate": "1991-02-02",
            "city": "New City",
            "country": "Old Country",  # new_country None → old value used
        }
    ]

    supabase_client.table.return_value.update.return_value \
        .eq.return_value \
        .execute.return_value = MockSupabaseResponse(data=updated_data)

    profiles = Profiles(supabase_client)

    result = profiles.update_profile_by_id(
        "user_123",
        new_full_name=None,
        new_birth_date="1991-02-02",
        new_city="New City",
        new_country=None,
        old_full_name=old_profile["full_name"],
        old_birth_date=old_profile["birthdate"],
        old_city=old_profile["city"],
        old_country=old_profile["country"],
    )

    assert result.data == updated_data

def test_delete_profile_by_id(supabase_client):
    deleted_data = [{"id": "user_123"}]

    supabase_client.table.return_value.delete.return_value \
        .eq.return_value \
        .execute.return_value = MockSupabaseResponse(data=deleted_data)

    profiles = Profiles(supabase_client)

    result = profiles.delete_profile_by_id("user_123")

    assert result.data == deleted_data

def test_get_all_profiles_raises_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .select.return_value \
        .neq.return_value \
        .execute.side_effect = Exception("DB down")

    profiles = Profiles(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        profiles.get_all_profiles("admin_123")

    assert "Failed to retrieve profiles" in str(exc.value)
        
def test_get_profile_by_id_raises_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .execute.side_effect = Exception("DB down")

    profiles = Profiles(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        profiles.get_profile_by_id("admin_123")

    assert "Failed to retrieve profile" in str(exc.value)

def test_create_profile_raises_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .insert.return_value \
        .execute.side_effect = Exception("DB down")
    
    profiles = Profiles(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        profiles.create_profile("user-123", "test_name", "1900-01-01", "test_city", "test_country")

    assert "Failed to create profile" in str(exc.value)

def test_update_profile_by_id_raises_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .update.return_value \
        .execute.side_effect = Exception("DB down")

    profiles = Profiles(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        profiles.update_profile_by_id("user-123", "new_test_name", "2025-01-01", "new_test_city", "new_test_country",
        "old_test_name", "1900-01-01", "old_test_city", "old_test_country")

    assert "Failed to update profile" in str(exc.value)

def test_delete_profile_by_id_raises_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .delete.return_value \
        .execute.side_effect = Exception("DB down")

    profiles = Profiles(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        profiles.delete_profile_by_id("user-123")

    assert "Failed to delete profile" in str(exc.value)



