import pytest
from unittest.mock import MagicMock
from database.questions import Questions

class MockSupabaseResponse:
    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error

@pytest.fixture
def supabase_client():
    client = MagicMock()

    query = MagicMock()
    query.eq.return_value = query

    client.table.return_value.select.return_value = query
    client.table.return_value.insert.return_value = query

    return client

def test_get_questions_by_questionnaire_id(supabase_client):
    expected_data = [
        {
            "id": "q_1",
            "question_text": "The app is very useful",
            "category": "Perceived Usefulness"
        }
    ]

    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .execute.return_value = MockSupabaseResponse(data=expected_data)

    questions = Questions(supabase_client)

    result = questions.get_questions_by_questionnaire_id("q_123")

    assert result.data == expected_data

def test_create_questions(supabase_client):
    inserted_data = [
        {
            "questionnaire_id": "q_123",
            "question_text":  "The app is very useful",
            "position": 1,
            "category": "Perceived Usefulness",
            "is_custom": False,
            "is_negative": False
        }
    ]

    supabase_client.table.return_value \
        .insert.return_value \
        .execute.return_value = MockSupabaseResponse(data=inserted_data)
    
    questions = Questions(supabase_client)

    result = questions.create_questions(inserted_data)

    assert result.data == inserted_data

def test_get_questions_by_questionnaire_id_raises_runtime_error(supabase_client):

    supabase_client.table.return_value \
        .select.return_value \
        .eq.return_value \
        .execute.side_effect = Exception("DB down")

    questions = Questions(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        questions.get_questions_by_questionnaire_id("q_123")

    assert "Failed to retrieve questions" in str(exc.value)

def test_create_questions_raises_runtime_error(supabase_client):

    supabase_client.table.return_value \
        .insert.return_value \
        .execute.side_effect = Exception("DB down")

    questions = Questions(supabase_client)

    with pytest.raises(RuntimeError) as exc:
        questions.create_questions([
            {
                "questionnaire_id": "q_123",
                "question_text":  "The app is very useful",
                "position": 1,
                "category": "Perceived Usefulness",
                "is_custom": False,
                "is_negative": False
            }
        ])

    assert "Failed to create the questions" in str(exc.value)

