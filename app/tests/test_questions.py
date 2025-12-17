import pytest
from unittest.mock import MagicMock
from database.questions import Questions

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

def test_get_questions_by_questionnaire_id(mock_supabase_client):
    questions = Questions(mock_supabase_client)

    result = questions.get_questions_by_questionnaire_id("q_123")

    mock_supabase_client.table.assert_called_once_with("questions")
    mock_supabase_client.table().select.assert_called_once_with("id, question_text")
    mock_supabase_client.table().select().eq.assert_any_call("questionnaire_id", "q_123")
    mock_supabase_client.table().select().execute.assert_called_once()

    assert result == {"data": "mocked_result"}

def test_create_questions(mock_supabase_client):
    questions = Questions(mock_supabase_client)
    questions_list = [
        {"questionnaire_id": "q-123", "question_text": "Using TestApp improves my work performance.", "position": 1},
        {"questionnaire_id": "q-123", "question_text": "TestApp improves the results of my work.", "position": 2},
        {"questionnaire_id": "q-123", "question_text": "I found TestApp useful.", "position": 3},
    ]

    result = questions.create_questions(questions_list)

    mock_supabase_client.table.assert_called_once_with("questions")
    mock_supabase_client.table().insert.assert_called_once_with(questions_list)
    mock_supabase_client.table().insert().execute.assert_called_once()

    assert result == {"data": "mocked_result"}

def test_get_questions_by_questionnaire_id_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    questions = Questions(mock_supabase_client)

    with pytest.raises(RuntimeError, match="Failed to retrieve questions"):
        questions.get_questions_by_questionnaire_id("q-123")

def test_create_questions_raises_runtime_error(mock_supabase_client):
    mock_supabase_client.table.side_effect = Exception("DB down")
    questions = Questions(mock_supabase_client)
    questions_list = [
        {"questionnaire_id": "q-123", "question_text": "Using TestApp improves my work performance.", "position": 1},
        {"questionnaire_id": "q-123", "question_text": "TestApp improves the results of my work.", "position": 2},
        {"questionnaire_id": "q-123", "question_text": "I found TestApp useful.", "position": 3},
    ]

    with pytest.raises(RuntimeError, match="Failed to create the questions"):
        questions.create_questions(questions_list)

