import pytest
from unittest.mock import MagicMock
from database.questionnaires import Questionnaires


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
    client.rpc.return_value = query
    client.table.return_value.delete.return_value = query

    return client


def test_get_all_questionnaires(supabase_client):
    expected_data = [
        {
            "id": "q_123",
            "title": "q_title",
            "details": "q_desc",
            "created_at": "2026-01-05 23:23:34.773619+00",
            "created_by": "admin_123"
        }
    ]

    supabase_client.table.return_value \
        .select.return_value \
        .order.return_value \
        .execute.return_value = MockSupabaseResponse(data=expected_data)

    questionnaires = Questionnaires(supabase_client)

    result = questionnaires.get_all_questionnaires()

    assert result.data == expected_data


def test_get_all_questionnaires_with_admin_response(supabase_client):
    expected_data = [
        {
            "id": "q_1",
            "title": "Questionnaire 1",
            "created_at": "2026-01-20T12:00:00Z",
            "responses": [
                {
                    "id": "r_1",
                    "user_id": "admin_123",
                    "questionnaire_id": "q_1",
                    "is_submitted": True
                }
            ]
        }
    ]

    supabase_client.table.return_value.select.return_value \
        .eq.return_value \
        .eq.return_value \
        .order.return_value \
        .execute.return_value = MockSupabaseResponse(data=expected_data)

    questionnaires = Questionnaires(supabase_client)

    result = questionnaires.get_all_questionnaires_with_admin_response(
        "admin_123"
    )

    assert result.data == expected_data


def test_get_questionnaire_by_id(supabase_client):
    expected_data = [
        {
            "id": "q_123",
            "title": "q_title",
            "details": "q_desc",
            "created_at": "2026-01-05 23:23:34.773619+00",
        }
    ]

    supabase_client.table.return_value.select.return_value \
        .eq.return_value \
        .order.return_value \
        .execute.return_value = MockSupabaseResponse(data=expected_data)

    questionnaires = Questionnaires(supabase_client)

    result = questionnaires.get_questionnaire_by_id("q_123")

    assert result.data == expected_data


def test_get_questionnaires_without_user_response(supabase_client):
    expected_data = [
        {
            "id": "q_1",
            "title": "Questionnaire 1",
            "details": "q_1_desc",
            "created_at": "2026-01-05 23:23:34.773619+00",
            "created_by": "admin_1"
        },
        {
            "id": "q_2",
            "title": "Questionnaire 2",
            "details": "q_2_desc",
            "created_at": "2026-01-05 23:23:34.773619+00",
            "created_by": "admin_2"
        },
    ]

    supabase_client.rpc.return_value.execute.return_value = (
        MockSupabaseResponse(data=expected_data)
    )

    questionnaires = Questionnaires(supabase_client)

    result = questionnaires.get_questionnaires_without_user_response(
        "user_123"
    )

    assert result.data == expected_data


def test_create_questionnaires(supabase_client):
    inserted_data = [
        {
            "title": "App TAM Questionnaire",
            "details": "q_details",
            "created_by": "admin_123"
        }
    ]

    supabase_client.table.return_value \
        .insert.return_value \
        .execute.return_value = MockSupabaseResponse(data=inserted_data)

    questionnaires = Questionnaires(supabase_client)

    result = questionnaires.create_questionnaire(
        "App",
        "q_details",
        "admin_123"
    )

    assert result.data == inserted_data


def test_delete_questionnaire_by_id(supabase_client):
    deleted_data = [{"questionnaire_id": "q_123"}]

    supabase_client.table.return_value.delete.return_value \
        .eq.return_value \
        .execute.return_value = MockSupabaseResponse(data=deleted_data)

    questionnaires = Questionnaires(supabase_client)

    result = questionnaires.delete_questionnaire_by_id("q_123")

    assert result.data == deleted_data


def test_get_all_questionnaires_raises_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .select.return_value \
        .order.return_value \
        .execute.side_effect = Exception("DB down")

    questionnaires = Questionnaires(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        questionnaires.get_all_questionnaires()

    assert "Failed to retrieve questionnaires" in str(exc.value)


def test_get_all_questionnaires_with_admin_response_raises_runtime_error(
    supabase_client
):
    supabase_client.table.return_value.select.return_value \
        .eq.return_value \
        .eq.return_value \
        .order.return_value \
        .execute.side_effect = Exception("DB down")

    questionnaires = Questionnaires(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        questionnaires.get_all_questionnaires_with_admin_response("user_123")

    assert "Failed to retrieve questionnaires" in str(exc.value)


def test_get_questionnaire_by_id_raises_runtime_error(supabase_client):
    supabase_client.table.return_value.select.return_value \
        .eq.return_value \
        .order.return_value \
        .execute.side_effect = Exception("DB down")

    questionnaires = Questionnaires(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        questionnaires.get_questionnaire_by_id("q-123")

    assert "Failed to retrieve questionnaire" in str(exc.value)


def test_get_questionnaires_without_user_response_raises_runtime_error(
    supabase_client
):
    supabase_client.rpc.return_value.execute.side_effect = Exception("DB down")

    questionnaires = Questionnaires(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        questionnaires.get_questionnaires_without_user_response("q-123")

    assert "Failed to retrieve questionnaires" in str(exc.value)


def test_create_questionnaires_raises_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .insert.return_value \
        .execute.side_effect = Exception("DB down")

    questionnaires = Questionnaires(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        questionnaires.create_questionnaire("App", "Details", "admin")

    assert "Failed to create questionnaire" in str(exc.value)


def test_delete_questionnaire_raises_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .delete.return_value \
        .execute.side_effect = Exception("DB down")

    questionnaires = Questionnaires(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        questionnaires.delete_questionnaire_by_id("q-123")

    assert "Failed to delete questionnaire" in str(exc.value)
