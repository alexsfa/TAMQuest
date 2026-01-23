import pytest
from unittest.mock import MagicMock
from database.answers import Answers


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
    client.table.return_value.upsert.return_value = query

    return client


def test_get_answers_by_response_id(supabase_client):
    expected_data = [
        {
            "id": "a1",
            "response_id": "res_123",
            "questions": {"question_text": "The app is useful", "position": 1},
            "likert_scale_options": {"label": "Agree", "value": 4},
        }
    ]

    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .order.return_value \
        .execute.return_value = MockSupabaseResponse(data=expected_data)

    answers = Answers(supabase_client)

    result = answers.get_answers_by_response_id("res_123")

    assert result.data == expected_data


def test_get_submitted_answers_by_questionnaire_id(supabase_client):
    expected_data = [
        {
            "response_id": "res_123",
            "responses": {"is_submitted": True},
            "questions": {
                "questionnaire_id": "q_123",
                "question_text": "The app is useful",
                "category": "Perceived Usefulness",
                "is_custom": False,
                "is_negative": False,
            },
            "likert_scale_options": {"label": "Agree", "value": 4},
        }
    ]

    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .eq.return_value \
        .execute.return_value = MockSupabaseResponse(data=expected_data)

    answers = Answers(supabase_client)

    result = answers.get_submitted_answers_by_questionnaire_id("q_123")

    assert result.data == expected_data


def test_create_answers(supabase_client):
    input_answers = [
        {
            "response_id": "res_123",
            "question_id": "q_1",
            "selected_option": "l_s_o_1",
        }
    ]

    inserted_data = [
        {
            "id": "a_1",
            **input_answers[0],
        }
    ]

    supabase_client.table.return_value \
        .insert.return_value \
        .execute.return_value = MockSupabaseResponse(data=inserted_data)

    answers = Answers(supabase_client)

    result = answers.create_answers(input_answers)

    assert result.data == inserted_data


def test_update_answers(supabase_client):
    input_answers = [
        {
            "response_id": "res_123",
            "question_id": "q_1",
            "selected_option": "l_s_o_2",
        }
    ]

    updated_data = [
        {
            "id": "a_1",
            **input_answers[0],
        }
    ]

    supabase_client.table.return_value \
        .upsert.return_value \
        .execute.return_value = MockSupabaseResponse(data=updated_data)

    answers = Answers(supabase_client)

    result = answers.update_answers(input_answers)

    assert result.data == updated_data


def test_get_answers_by_response_id_raises_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .order.return_value \
        .execute.side_effect = Exception("DB is down")

    answers = Answers(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        answers.get_answers_by_response_id("res_123")

    assert "Failed to retrieve answers" in str(exc.value)


def test_get_submitted_answers_by_questionnaire_id_raises_runtime_error(
    supabase_client
):
    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .eq.return_value \
        .execute.side_effect = Exception("DB is down")

    answers = Answers(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        answers.get_submitted_answers_by_questionnaire_id("q_123")

    assert "Failed to retrieve answers" in str(exc.value)


def test_create_answers_raises_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .insert.return_value \
        .execute.side_effect = Exception("DB down")

    answers = Answers(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        answers.create_answers([{"response_id": "res_123"}])

    assert "Failed to insert the answers" in str(exc.value)


def test_update_answers_raises_runtime_error(supabase_client):
    supabase_client.table.return_value \
        .upsert.return_value \
        .execute.side_effect = Exception("DB down")

    answers = Answers(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        answers.update_answers([{"response_id": "res_123"}])

    assert "Failed to update the answers" in str(exc.value)
