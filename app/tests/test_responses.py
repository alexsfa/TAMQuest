import pytest
from unittest.mock import MagicMock
from database.responses import Responses


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
    client.rpc.return_value = query
    client.table.return_value.delete.return_value = query

    return client


def test_get_all_responses(supabase_client):
    expected_data = [
        {
            "questionnaires": {
                "id": "q_123",
                "title": "q_title",
                "details": "q_details",
                "created_at": "2026-01-16 12:06:11.061732+00",
                "created_by": "admin_123"
            },
            "profiles": {
                "full_name": "user_name"
            },
            "id": "res_123",
            "submitted_at": "2026-01-07 18:24:39.412808+00",
            "is_submitted": True
        }
    ]

    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .order.return_value \
        .execute.return_value = MockSupabaseResponse(data=expected_data)

    responses = Responses(supabase_client)

    result = responses.get_all_responses()

    assert result.data == expected_data


def test_get_all_responses_by_questionnaire_id(supabase_client):
    expected_data = [
        {
            "questionnaires": {
                "id": "q_123",
                "title": "q_title",
                "details": "q_details",
                "created_at": "2026-01-16 12:06:11.061732+00",
                "created_by": "admin_123"
            },
            "profiles": {
                "full_name": "user_name"
            },
            "id": "res_123",
            "submitted_at": "2026-01-07 18:24:39.412808+00",
            "is_submitted": True
        }
    ]

    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .eq.return_value \
        .execute.return_value = MockSupabaseResponse(data=expected_data)

    responses = Responses(supabase_client)

    result = responses.get_all_responses_by_questionnaire_id("q_123")

    assert result.data == expected_data


def test_get_response_by_id(supabase_client):
    expected_data = [
        {
            "questionnaires": {
                "id": "q_123",
                "title": "q_title",
                "details": "q_details",
                "created_at": "2026-01-16 12:06:11.061732+00",
            },
            "profiles": {
                "full_name": "user_name"
            },
            "submitted_at": "2026-01-07 18:24:39.412808+00",
        }
    ]

    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .execute.return_value = MockSupabaseResponse(data=expected_data)

    responses = Responses(supabase_client)

    result = responses.get_response_by_id("res_123")

    assert result.data == expected_data


def test_get_response_by_user_id(supabase_client):

    expected_data = [
        {
            "questionnaires": {
                "id": "q_123",
                "title": "q_title",
                "details": "q_details",
                "created_at": "2026-01-16 12:06:11.061732+00",
                "created_by": "admin_123"
            },
            "id": "res_123",
            "submitted_at": "2026-01-07 18:24:39.412808+00",
            "is_submitted": True
        }
    ]

    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .order.return_value \
        .execute.return_value = MockSupabaseResponse(data=expected_data)

    responses = Responses(supabase_client)

    result = responses.get_response_by_user_id("user_123")

    assert result.data == expected_data


def test_get_responses_by_questionnaire_id_with_is_submitted_none(
    supabase_client
):

    expected_data = [{"id": "res_123"}]

    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .eq.return_value \
        .eq.return_value \
        .execute.return_value = MockSupabaseResponse(data=expected_data)

    responses = Responses(supabase_client)

    result = responses.get_responses_by_questionnaire_id(
        user_id="user_123",
        questionnaire_id="q_123",
        is_submitted=None
    )

    assert result.data == expected_data


def test_get_responses_by_questionnaire_id_with_is_submitted(supabase_client):

    expected_data = [{"id": "res_123"}]

    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .eq.return_value \
        .execute.return_value = MockSupabaseResponse(data=expected_data)

    responses = Responses(supabase_client)

    result = responses.get_responses_by_questionnaire_id(
        user_id="user_123",
        questionnaire_id="q_123",
        is_submitted=True
    )

    assert result.data == expected_data


def test_get_response_by_questionnaire_title(supabase_client):
    expected_data = [{"id": "res_123"}]

    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .order.return_value \
        .execute.return_value = MockSupabaseResponse(data=expected_data)

    responses = Responses(supabase_client)

    result = responses.get_responses_by_questionnaire_title("q_title")

    assert result.data == expected_data


def test_get_all_responses_category_means(supabase_client):

    expected_data = [
        {
            "answers": {
                "response_id": "res_123"
            },
            "questions": {
                "category": "Perceived Usedfulness"
            },
            "mean_score": 4.5
        }
    ]

    supabase_client.rpc.return_value.execute.return_value = (
        MockSupabaseResponse(data=expected_data)
    )
    responses = Responses(supabase_client)

    result = responses.get_all_responses_category_means("q_123")

    assert result.data == expected_data


def test_create_response(supabase_client):
    inserted_data = [
        {
            "user_id": "user_123",
            "questionnaire_id": "q_123",
            "is_submitted": True
        }
    ]

    supabase_client.table.return_value \
        .insert.return_value \
        .execute.return_value = MockSupabaseResponse(data=inserted_data)

    responses = Responses(supabase_client)

    result = responses.create_response("user_123", "q_123", True)

    assert result.data == inserted_data


def test_update_response_on_submitted(supabase_client):
    updated_data = [{"is_submitted": True}]

    supabase_client.table.return_value \
        .update.return_value \
        .execute.return_value = MockSupabaseResponse(data=updated_data)

    responses = Responses(supabase_client)

    result = responses.update_response_on_submitted("user_123", True)

    assert result.data == updated_data


def test_delete_response_by_id(supabase_client):
    deleted_data = [{"id": "res_123"}]

    supabase_client.table.return_value \
        .delete.return_value \
        .execute.return_value = MockSupabaseResponse(data=deleted_data)

    responses = Responses(supabase_client)

    result = responses.delete_response_by_id("res_123")

    assert result.data == deleted_data


def test_get_all_responses_raise_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .order.return_value \
        .execute.side_effect = Exception("DB down")

    responses = Responses(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        responses.get_all_responses()

    assert "Failed to retrieve responses" in str(exc.value)


def test_get_all_responses_by_questionnaire_id_raise_runtime_error(
    supabase_client
):
    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .eq.return_value \
        .execute.side_effect = Exception("DB down")

    responses = Responses(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        responses.get_all_responses_by_questionnaire_id("q_123")

    assert "Failed to retrieve responses by questionnaire" in str(exc.value)


def test_get_response_by_id_raise_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .execute.side_effect = Exception("DB down")

    responses = Responses(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        responses.get_response_by_id("res_123")

    assert "Failed to retrieve response" in str(exc.value)


def test_get_response_by_user_id_raise_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .order.return_value \
        .execute.side_effect = Exception("DB down")

    responses = Responses(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        responses.get_response_by_user_id("user_123")

    assert "Failed to retrieve response" in str(exc.value)


def test_get_responses_by_questionnaire_id_raise_runtime_error(
    supabase_client
):

    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .eq.return_value \
        .eq.return_value \
        .execute.side_effect = Exception("DB down")

    responses = Responses(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        responses.get_responses_by_questionnaire_id("user_123", "q_123", True)

    assert "Failed to retrieve the specified draft" in str(exc.value)


def test_get_response_by_questionnaire_title_raise_runtime_error(
    supabase_client
):

    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .eq.return_value \
        .order.return_value \
        .execute.side_effect = Exception("DB down")

    responses = Responses(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        responses.get_responses_by_questionnaire_title("q_title")

    assert "Failed to retrieve responses" in str(exc.value)


def test_get_all_responses_category_means_raise_runtime_error(supabase_client):
    supabase_client.rpc.return_value.execute.side_effect = Exception("DB down")

    responses = Responses(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        responses.get_all_responses_category_means("q_123")

    assert (
        "Failed to retrieve the category means from the responses"
        in str(exc.value)
    )


def test_create_response_raise_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .insert.return_value \
        .execute.side_effect = Exception("DB down")

    responses = Responses(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        responses.create_response("user_123", "q_123", True)

    assert "Failed to create response" in str(exc.value)


def test_update_response_on_submitted_raise_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .update.return_value \
        .execute.side_effect = Exception("DB down")

    responses = Responses(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        responses.update_response_on_submitted("user_123", True)

    assert "Failed to update response" in str(exc.value)


def test_delete_response_by_id_raise_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .delete.return_value \
        .execute.side_effect = Exception("DB down")

    responses = Responses(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        responses.delete_response_by_id("res_123")

    assert "Failed to delete response" in str(exc.value)
