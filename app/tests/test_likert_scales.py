import pytest
from unittest.mock import MagicMock
from database.likert_scales import Likert_scales

@pytest.fixture
def mock_supabase_client():
    client = MagicMock()
    table = MagicMock()
    query = MagicMock()

    client.table.return_value = table
    table.select.return_value = query
    table.insert.return_value = query

    query.eq.return_value = query

    query.execute.return_value = {"data": "mocked_result"}

    return client

def test_get_likert_scale_by_questionnaire_id(mock_supabase_client):
    likert_scales_repo = Likert_scales(mock_supabase_client)

    mock_supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .execute.return_value = {"data": "mocked_result"}

    result = likert_scales_repo.get_likert_scale_by_questionnaire_id("q_123")

    mock_supabase_client.table.assert_called_once_with("likert_scales")
    mock_supabase_client.table().select.assert_called_once_with("id")
    mock_supabase_client.table().select().eq.assert_any_call("questionnaire_id", "q_123")
    mock_supabase_client.table().select().eq().execute.assert_called_once()

    assert result["data"] == "mocked_result"

def test_create_likert_scale(mock_supabase_client):
    likert_scales_repo = Likert_scales(mock_supabase_client)

    result = likert_scales_repo.create_likert_scale(
        questionnaire_id = "q_123"
    )

    mock_supabase_client.table.assert_called_once_with("likert_scales")
    mock_supabase_client.table().insert.assert_called_once_with({
        "questionnaire_id": "q_123"
    })
    mock_supabase_client.table().insert().execute.assert_called_once()

    assert isinstance(result, dict)
    assert result["data"] == "mocked_result"

def test_get_likert_scale_by_questionnaire_id_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    likert_scales_repo = Likert_scales(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to retrieve the questionnaire's likert scale"):
        likert_scales_repo.get_likert_scale_by_questionnaire_id("user-123")

def test_create_likert_scale_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down") 
    likert_scales_repo = Likert_scales(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to create the questionnaire's likert scale"):
        likert_scales_repo.create_likert_scale("l_s_123")
