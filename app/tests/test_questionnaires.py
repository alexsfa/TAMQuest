import pytest
from unittest.mock import MagicMock
from database.questionnaires import Questionnaires

@pytest.fixture
def mock_supabase_client():
    client = MagicMock()
    table = MagicMock()
    query = MagicMock()

    client.table.return_value = table
    client.rpc.return_value = query
    table.select.return_value = query
    table.insert.return_value = query
    table.delete.return_value = query

    query.eq.return_value = query
    query.order.return_value = query

    query.execute.return_value = {"data": "mocked_result"}

    return client


def test_get_all_questionnaires(mock_supabase_client):
    questionnaires = Questionnaires(mock_supabase_client)

    result = questionnaires.get_all_questionnaires()

    mock_supabase_client.table.assert_called_once_with("questionnaires")
    mock_supabase_client.table().select.assert_called_once()
    mock_supabase_client.table().select().order.assert_called_once_with("created_at", desc=True)
    mock_supabase_client.table().select().order().execute.assert_called_once()

    assert result["data"] == "mocked_result"

def test_get_all_questionnaires_without_admin_response(mock_supabase_client):
    questionnaires = Questionnaires(mock_supabase_client)

    result = questionnaires.get_all_questionnaires_without_admin_response("user_123")

    query = mock_supabase_client.table.return_value.select.return_value

    mock_supabase_client.table.assert_called_once_with("questionnaires")
    mock_supabase_client.table().select.assert_called_once_with(
                    f"""
                    *,
                    responses!left(
                        id,
                        user_id,
                        questionnaire_id,
                        is_submitted
                    )
                    """
    )

    select_arg = mock_supabase_client.table().select.call_args.args[0]

    assert "responses!left" in select_arg
    assert "questionnaire_id" in select_arg
    assert "is_submitted" in select_arg

    eq_calls = [call.args for call in query.eq.call_args_list]
    assert ("responses.user_id", "user_123") in eq_calls
    assert ("responses.is_submitted", True) in eq_calls

    query.order.assert_called_once_with("created_at", desc=True)
    query.execute.assert_called_once()

    assert result["data"] == "mocked_result"

def test_get_questionnaire_by_id(mock_supabase_client):
    questionnaires = Questionnaires(mock_supabase_client)

    result = questionnaires.get_questionnaire_by_id("q-123")

    mock_supabase_client.table.assert_called_once_with("questionnaires")
    mock_supabase_client.table().select.assert_called_once_with( "id, title, details, created_at" )
    mock_supabase_client.table().select().eq.assert_called_once_with("id", "q-123")
    mock_supabase_client.table().select().execute.assert_called_once()

    assert result["data"] == "mocked_result"


def test_get_questionnaires_without_user_response(mock_supabase_client):
    mock_supabase_client.rpc.return_value.execute.return_value = {"data": []}
    questionnaires = Questionnaires(mock_supabase_client)

    result = questionnaires.get_questionnaires_without_user_response("user-123")

    mock_supabase_client.rpc.assert_called_once_with(
        "questionnaires_without_user_response",
        {"uid": "user-123"}
    )

    mock_supabase_client.rpc().execute.assert_called_once()

    assert result == {"data":[]}


def test_create_questionnaires(mock_supabase_client):
    questionnaires = Questionnaires(mock_supabase_client)

    result = questionnaires.create_questionnaire(
        app_name="TestApp",
        questionnaire_details="Details",
        user_id="admin-123"
    )

    mock_supabase_client.table.assert_called_once_with("questionnaires")
    mock_supabase_client.table().insert.assert_called_once_with({
        "title": "TestApp TAM Questionnaire",
        "details": "Details",
        "created_by": "admin-123"
    })
    mock_supabase_client.table().insert().execute.assert_called_once()

    assert result["data"] == "mocked_result"


def test_delete_questionnaire_by_id(mock_supabase_client):
    questionnaires = Questionnaires(mock_supabase_client)

    result = questionnaires.delete_questionnaire_by_id("q-123")

    mock_supabase_client.table.assert_called_once_with("questionnaires")
    mock_supabase_client.table().delete.assert_called_once()
    mock_supabase_client.table().delete().eq.assert_called_once_with("id", "q-123")
    mock_supabase_client.table().delete().eq().execute.assert_called_once()

    assert result["data"] == "mocked_result"


def test_get_all_questionnaires_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    questionnaires = Questionnaires(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to retrieve questionnaires"):
        questionnaires.get_all_questionnaires()

def test_get_all_questionnaires_without_admin_response_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    questionnaires = Questionnaires(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to retrieve questionnaires"):
        questionnaires.get_all_questionnaires_without_admin_response("user_123")


def test_get_questionnaire_by_id_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    questionnaires = Questionnaires(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to retrieve questionnaire"):
        questionnaires.get_questionnaire_by_id("q-123")


def test_get_questionnaires_without_user_response_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.rpc.side_effect = Exception("DB down")
    questionnaires = Questionnaires(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to retrieve questionnaires"):
        questionnaires.get_questionnaires_without_user_response("q-123")


def test_create_questionnaires_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    questionnaires = Questionnaires(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to create questionnaire"):
        questionnaires.create_questionnaire("App", "Details", "admin")


def test_delete_questionnaire_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    questionnaires = Questionnaires(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to delete questionnaire"):
        questionnaires.delete_questionnaire_by_id("q-123")


       