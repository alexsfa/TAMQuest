import pytest
from unittest.mock import MagicMock
from database.responses import Responses

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
    query.order.return_value = query

    query.execute.return_value = {"data": "mocked_result"}

    return client

def test_get_all_responses(mock_supabase_client):
    responses = Responses(mock_supabase_client)

    result = responses.get_all_responses()

    mock_supabase_client.table.assert_called_once_with("responses")
    mock_supabase_client.table().select.assert_called_once()
    mock_supabase_client.table().select().eq.assert_any_call("is_submitted", True)
    mock_supabase_client.table().select().execute.assert_called_once()

    assert result == {"data": "mocked_result"}

def test_get_response_by_id(mock_supabase_client):
    responses = Responses(mock_supabase_client)

    result = responses.get_response_by_id("res_123")

    mock_supabase_client.table.assert_called_once_with("responses")
    mock_supabase_client.table().select.assert_called_once_with(
        "questionnaires(id, title, details, created_at), profiles(full_name), submitted_at"
    )
    mock_supabase_client.table().select().eq.assert_called_once_with("id", "res_123")
    mock_supabase_client.table().select().execute.assert_called_once()

    assert result == {"data": "mocked_result"}

def test_get_response_by_user_id(mock_supabase_client):
    responses = Responses(mock_supabase_client)

    result = responses.get_response_by_user_id("user_123")
    mock_supabase_client.table().select.assert_called_once_with("questionnaires(*), id, submitted_at, is_submitted")
    mock_supabase_client.table().select().eq.assert_called_once_with("user_id", "user_123")
    mock_supabase_client.table().select().execute.assert_called_once()

    assert result == {"data": "mocked_result"}

def test_get_responses_by_questionnaire_id(mock_supabase_client):
    responses = Responses(mock_supabase_client)

    result = responses.get_responses_by_questionnaire_id("user_123", "q_123", True)

    mock_supabase_client.table.assert_called_once_with("responses")
    mock_supabase_client.table().select.assert_called_once_with("id")
    mock_supabase_client.table().select().eq.assert_any_call("user_id", "user_123")
    mock_supabase_client.table().select().eq.assert_any_call("questionnaire_id", "q_123")
    mock_supabase_client.table().select().execute.assert_called_once()

    assert result == {"data": "mocked_result"}

def test_create_response(mock_supabase_client):
    responses = Responses(mock_supabase_client)

    result = responses.create_response("user_123", "q_123", True)

    mock_supabase_client.table.assert_called_once_with("responses")
    mock_supabase_client.table().insert.assert_called_once_with({
        "user_id": "user_123",
        "questionnaire_id": "q_123", 
        "is_submitted": True
    })
    mock_supabase_client.table().insert().execute.assert_called_once()

    assert result == {"data": "mocked_result"}

def test_update_response_on_submitted(mock_supabase_client):
    responses = Responses(mock_supabase_client)

    result = responses.update_response_on_submitted("user_123", True)

    mock_supabase_client.table.assert_called_once_with("responses")
    mock_supabase_client.table().update.assert_called_once_with({"is_submitted": True})
    mock_supabase_client.table().update().eq.assert_called_once_with("user_id", "user_123")
    mock_supabase_client.table().update().execute.assert_called_once()

    assert result == {"data": "mocked_result"}

def test_delete_response_by_id(mock_supabase_client):
    responses = Responses(mock_supabase_client)

    result = responses.delete_response_by_id("res_123")
    
    mock_supabase_client.table.assert_called_once_with("responses")
    mock_supabase_client.table().delete.assert_called_once()
    mock_supabase_client.table().delete().eq.assert_called_once_with("id", "res_123")
    mock_supabase_client.table().delete().execute.assert_called_once()

    assert result == {"data": "mocked_result"}

def test_get_all_responses_raise_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    responses = Responses(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to retrieve responses"):
        responses.get_all_responses()

def test_get_response_by_id_raise_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    responses = Responses(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to retrieve response"):
        responses.get_response_by_id("res_123")

def test_get_response_by_user_id_raise_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    responses = Responses(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to retrieve response"):
        responses.get_response_by_user_id("user_123")

def test_get_responses_by_questionnaire_id_raise_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    responses = Responses(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to retrieve the specified draft"):
        responses.get_responses_by_questionnaire_id("uer_123", "q_123", True)

def test_create_response_raise_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    responses = Responses(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to create response"):
        responses.create_response("user_123", "q_123", True)

def test_update_response_on_submitted(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    responses = Responses(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to update response"):
        responses.update_response_on_submitted("user_123", True)

def test_delete_response_by_id(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    responses = Responses(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to delete response"):
        responses.delete_response_by_id("res_123")




