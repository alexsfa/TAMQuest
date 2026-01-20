import pytest
from unittest.mock import MagicMock
from database.likert_scales import Likert_scales

class MockSupabaseResponse:
    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error

@pytest.fixture
def supabase_client():
    client = MagicMock()

    query = MagicMock()
    query.eq.return_value = query
    query.order.return_value = query

    client.table.return_value.select.return_value = query
    client.table.return_value.insert.return_value = query
    client.table.return_value.update.return_value = query

    return client

def test_get_likert_scale_by_questionnaire_id(supabase_client):
    expected_data = [
        {
            "id": "l_s_123",
        }
    ]
        
    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .execute.return_value = MockSupabaseResponse(data=expected_data)

    likert_scales = Likert_scales(supabase_client)

    result = likert_scales.get_likert_scale_by_questionnaire_id("q_123")

    assert result.data == expected_data

def test_create_likert_scale(supabase_client):
    inserted_data = [
        {
            "questionnaire_id": "q_123",
        }
    ]

    supabase_client.table.return_value \
        .insert.return_value \
        .execute.return_value = MockSupabaseResponse(data=inserted_data)

    likert_scales = Likert_scales(supabase_client)

    result = likert_scales.create_likert_scale({"questionnaire_id": "q_123"})

    assert result.data == inserted_data

def test_get_likert_scale_by_questionnaire_id_raises_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .order.return_value \
        .execute.side_effect = Exception("DB down")

    likert_scales = Likert_scales(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        likert_scales.get_likert_scale_by_questionnaire_id("q_123")

    assert "Failed to retrieve the questionnaire's likert scale" in str(exc.value)

def test_create_likert_scale_raises_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .insert.return_value \
        .execute.side_effect = Exception("DB down") 

    likert_scales = Likert_scales(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        likert_scales.create_likert_scale([{"questionnaire_id": "q_123"}])

    assert "Failed to create the questionnaire's likert scale" in str(exc.value)
