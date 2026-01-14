import pytest
from unittest.mock import MagicMock
from database.likert_scale_options import Likert_scale_options

@pytest.fixture
def mock_supabase_client():
    client = MagicMock()
    table = MagicMock()
    query = MagicMock()

    client.table.return_value = table
    table.select.return_value = query
    table.insert.return_value = query

    query.eq.return_value = query
    query.order.return_value = query

    query.execute.return_value = {"data": "mocked_result"}

    return client

def test_get_options_by_likert_scale_id(mock_supabase_client):
    likert_scales_options_repo = Likert_scale_options(mock_supabase_client)

    result = likert_scales_options_repo.get_options_by_likert_scale_id("l_s_123")

    mock_supabase_client.table.assert_called_once_with("likert_scale_options")
    mock_supabase_client.table().select.assert_called_once_with("id, value, label")
    mock_supabase_client.table().select().eq.assert_any_call("likert_scale_id", "l_s_123")
    mock_supabase_client.table().select().eq().order.assert_called_once_with("value")
    mock_supabase_client.table().select().eq().order().execute.assert_called_once()

    assert result["data"] == "mocked_result"

def test_create_likert_scale_options(mock_supabase_client):
    likert_scales_options_repo = Likert_scale_options(mock_supabase_client)
    likert_scale_options = [
        {"likert_scale_id": "l_s_123", "value": 1, "label": "Disagree"},
        {"likert_scale_id": "l_s_123", "value": 2, "label": "Neutral"},
        {"likert_scale_id": "l_s_123", "value": 3, "label": "Agree"}
    ]

    result = likert_scales_options_repo.create_likert_scale_options(likert_scale_options)

    mock_supabase_client.table.assert_called_once_with("likert_scale_options")
    mock_supabase_client.table().insert.assert_called_once_with(likert_scale_options)
    mock_supabase_client.table().insert().execute.assert_called_once()

    assert isinstance(result, dict)
    assert result["data"] == "mocked_result"

def test_get_options_by_likert_scale_id_fail(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    likert_scales_options_repo = Likert_scale_options(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to retrieve the likert scale's options"):
        likert_scales_options_repo.get_options_by_likert_scale_id("l_s_123")

def test_create_likert_scale_options_fail(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down") 
    likert_scales_options_repo = Likert_scale_options(mock_supabase_client)
    likert_scale_options = [
        {"likert_scale_id": "l_s_123", "value": 1, "label": "Disagree"},
        {"likert_scale_id": "l_s_123", "value": 2, "label": "Neutral"},
        {"likert_scale_id": "l_s_123", "value": 3, "label": "Agree"}
    ]

    with pytest.raises(RuntimeError, match="Failed to insert the likert scale's options"):
        likert_scales_options_repo.create_likert_scale_options(likert_scale_options)
