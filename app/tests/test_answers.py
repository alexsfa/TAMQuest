import pytest
from unittest.mock import MagicMock
from database.answers import Answers

@pytest.fixture
def mock_supabase_client():
    client = MagicMock()
    table = MagicMock()
    query = MagicMock()

    client.table.return_value = table
    table.select.return_value = query
    table.insert.return_value = query
    table.upsert.return_value = query

    query.eq.return_value = query
    query.order.return_value = query

    query.execute.return_value = {"data": "mocked_result"}

    return client

def test_get_answers_by_response_id(mock_supabase_client):
    answers = Answers(mock_supabase_client)

    result = answers.get_answers_by_response_id("res_123")

    mock_supabase_client.table.assert_called_once_with("answers")
    mock_supabase_client.table().select.assert_called_once_with("*, questions(question_text, position), likert_scale_options(label, value)")
    mock_supabase_client.table().select().eq.assert_any_call("response_id", "res_123")
    mock_supabase_client.table().select().order.assert_any_call("questions(position)")
    mock_supabase_client.table().select().execute.assert_called_once()

    assert result["data"] == "mocked_result"

def test_get_submitted_answers_by_questionnaire_id(mock_supabase_client):
    answers = Answers(mock_supabase_client)

    result = answers.get_submitted_answers_by_questionnaire_id("q_123")

    query = mock_supabase_client.table.return_value.select.return_value

    mock_supabase_client.table.assert_called_once_with("answers")
    mock_supabase_client.table().select.assert_called_once_with("response_id, responses!inner(is_submitted), questions!inner(questionnaire_id, question_text, category, is_custom, is_negative), likert_scale_options!inner(value, label)")
    
    eq_calls = [call.args for call in query.eq.call_args_list]
    assert ("questions.questionnaire_id", "q_123") in eq_calls
    assert ("responses.is_submitted", True) in eq_calls

    query.execute.assert_called_once()

    assert result["data"] == "mocked_result"

def test_create_answers(mock_supabase_client):
    answers = Answers(mock_supabase_client)
    answers_list = [
        {"response_id": "res_123","question_id": "q_1", "question_text": "question_1", "label": "Disagree", "value": 1 },
        {"response_id": "res_123","question_id": "q_2", "question_text": "question_2", "label": "Neutral", "value": 2 },
        {"response_id": "res_123","question_id": "q_3", "question_text": "question_3", "label": "Agree", "value": 3 },
    ]

    result = answers.create_answers(answers_list)

    mock_supabase_client.table.assert_called_once_with("answers")
    mock_supabase_client.table().insert.assert_called_once_with(answers_list)
    mock_supabase_client.table().insert().execute.assert_called_once()

    assert result["data"] == "mocked_result"

def test_update_answers(mock_supabase_client):
    answers = Answers(mock_supabase_client)
    answers_list = [
        {"response_id": "res_123","question_id": "q_1", "selected_option_value": "Agree"},
        {"response_id": "res_123","question_id": "q_2", "selected_option_value": "Agree"},
        {"response_id": "res_123","question_id": "q_3", "selected_option_value": "Agree"},
    ]

    result = answers.update_answers(answers_list)

    mock_supabase_client.table.assert_called_once_with("answers")
    mock_supabase_client.table().upsert.assert_called_once_with(
        answers_list,
        on_conflict=["response_id,question_id"]
    )
    mock_supabase_client.table().upsert().execute.assert_called_once()

    assert result["data"] == "mocked_result"

def test_get_answers_by_response_id_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    answers = Answers(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to retrieve answers"):
        answers.get_answers_by_response_id("res_123")

def test_get_submitted_answers_by_questionnaire_id_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    answers = Answers(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to retrieve answers"):
        answers.get_submitted_answers_by_questionnaire_id("q_123")

def test_create_answers_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    answers = Answers(mock_supabase_client)
    answers_list = [
        {"response_id": "res_123","question_id": "q_1", "selected_option_value": "Agree"},
        {"response_id": "res_123","question_id": "q_2", "selected_option_value": "Agree"},
        {"response_id": "res_123","question_id": "q_3", "selected_option_value": "Agree"},
    ]
    
    with pytest.raises(RuntimeError, match="Failed to insert the answers"):
        answers.create_answers(answers_list)

def test_update_answers_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    answers = Answers(mock_supabase_client)
    answers_list = [
        {"response_id": "res_123","question_id": "q_1", "selected_option_value": "Agree"},
        {"response_id": "res_123","question_id": "q_2", "selected_option_value": "Agree"},
        {"response_id": "res_123","question_id": "q_3", "selected_option_value": "Agree"},
    ]

    with pytest.raises(RuntimeError, match="Failed to update the answers"):
        answers.update_answers(answers_list)
