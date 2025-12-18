import pytest
from unittest.mock import MagicMock
from services.database_service import retrieve_questionnaire, retrieve_questionnaire_by_response, submit_questionnaire, retrieve_response_info

@pytest.fixture
def mock_streamlit(monkeypatch):
    fake_st = MagicMock()
    fake_st.session_state = {
        "app_name": "TestApp",
        "q_details": "Some details",
        "add_questions": False
    }

    monkeypatch.setattr("services.database_service.st", fake_st)
    return fake_st

@pytest.fixture
def mock_question_generators(monkeypatch):
    monkeypatch.setattr(
        "services.database_service.generate_tam_questions",
        lambda questions, app_name: {
            "Perceived Usefulleness": ["Question 1", "Question 2"]
        }
    )

    monkeypatch.setattr(
        "services.database_service.generate_additional_tam_questions",
        lambda questions, app_name: {}
    )

def test_retrieve_questionnaire():
    questionnaires_repo = MagicMock()
    questions_repo = MagicMock()
    logger = MagicMock()

    questionnaire_data = {"id": "q_123", "title": "Test Questionnaire","details": "description", "created_by": "user_123", "created_at": "2025-12-15 14:03:34.15619+00"}
    questions_data = {"data": [{"id": "1", "questionnnaire_id": "q_123", "question_text": "Question 1", "position": 1}]}

    questionnaires_repo.get_questionnaire_by_id.return_value = questionnaire_data
    questions_repo.get_questions_by_questionnaire_id.return_value = questions_data

    result = retrieve_questionnaire(
        "q_123",
        questionnaires_repo,
        questions_repo,
        logger
    )

    questionnaires_repo.get_questionnaire_by_id.assert_called_once_with("q_123")
    questions_repo.get_questions_by_questionnaire_id.assert_called_once_with("q_123")
    logger.error.assert_not_called()

    assert result == [questionnaire_data, questions_data]

def test_retrieve_questionnaire_by_response():
    responses_repo = MagicMock()
    questions_repo = MagicMock()
    logger = MagicMock()

    mock_response = MagicMock()
    mock_response.data = [{"questionnaires": {"id": "q_123"}}]
    responses_repo.get_response_by_id.return_value = mock_response

    mock_questions = {"data": [{"id": "1", "questionnaire_id": "q_123", "question_text": "Question 1", "position": 1}]}
    questions_repo.get_questions_by_questionnaire_id.return_value = mock_questions

    result = retrieve_questionnaire_by_response(
        "res_123",
        responses_repo,
        questions_repo,
        logger
    )

    responses_repo.get_response_by_id.assert_called_once_with("res_123")
    questions_repo.get_questions_by_questionnaire_id.assert_called_once_with("q_123")
    logger.error.assert_not_called()

    assert result == [mock_response, mock_questions]

def test_submit_questionnaire(mock_streamlit, mock_question_generators):
    questionnaires_repo = MagicMock()
    questions_repo = MagicMock()
    logger = MagicMock()

    mock_questionnaire = MagicMock()
    mock_questionnaire.data = [{"id": "q_123"}]

    questionnaires_repo.create_questionnaire.return_value = mock_questionnaire
    questions_repo.create_questions.return_value = {"data": "questions_inserted"}

    result = submit_questionnaire(
        "TestApp",
        "Some details",
        "user_123",
        questionnaires_repo,
        questions_repo,
        logger
    )

    questionnaires_repo.create_questionnaire.assert_called_once()
    questions_repo.create_questions.assert_called_once()

    inserted_questions = questions_repo.create_questions.call_args[0][0]
    assert len(inserted_questions) == 2
    assert inserted_questions[0]["position"] == 1
    assert inserted_questions[1]["position"] == 2

    assert result == [mock_questionnaire, {"data": "questions_inserted"}]


def test_retrieve_response_info():
    responses_repo = MagicMock()
    answers_repo = MagicMock()
    logger = MagicMock()

    mock_response = MagicMock()
    mock_response.data = [{"id": "res_123"}]
    responses_repo.get_response_by_id.return_value = mock_response

    mock_answers = {"data": [{ "id": "1", "response_id": "res_123", "question_id": "q_1", "selected_option_value": "Disagree" }]}
    answers_repo.get_answers_by_response_id.return_value = mock_answers

    result = retrieve_response_info(
        "res_123",
        responses_repo,
        answers_repo,
        logger
    )

    responses_repo.get_response_by_id.assert_called_once_with("res_123")
    answers_repo.get_answers_by_response_id.assert_called_once_with("res_123")
    logger.error.assert_not_called()

    assert result == [mock_response, mock_answers]


def test_retrieve_questionnaire_repo_fail():
    questionnaires_repo = MagicMock()
    questions_repo = MagicMock()
    logger = MagicMock()

    questionnaires_repo.get_questionnaire_by_id.side_effect = RuntimeError("DB error")

    result = retrieve_questionnaire(
        "q_123",
        questionnaires_repo,
        questions_repo,
        logger
    )

    questionnaires_repo.get_questionnaire_by_id.assert_called_once_with("q_123")
    logger.error.assert_called_once()

    questions_repo.get_questions_by_questionnaire_id.assert_not_called()

    assert result[0] is None
    assert result[1] is None

def test_retrieve_questionnaire_questions_repo_fail():
    questionnaires_repo = MagicMock()
    questions_repo = MagicMock()
    logger = MagicMock()

    mock_questionnaire = MagicMock()
    questionnaires_repo.get_questionnaire_by_id.return_value = mock_questionnaire

    questions_repo.get_questions_by_questionnaire_id.side_effect = RuntimeError("DB error")

    result = retrieve_questionnaire(
        "q_123",
        questionnaires_repo,
        questions_repo,
        logger
    )

    questionnaires_repo.get_questionnaire_by_id.assert_called_once_with("q_123")
    questions_repo.get_questions_by_questionnaire_id.assert_called_once_with("q_123")

    logger.error.assert_called_once_with("Database error: DB error")

    assert result[0] is mock_questionnaire
    assert result[1] is None

def test_retrieve_questionnaire_by_response_repo_fail():
    responses_repo = MagicMock()
    questions_repo = MagicMock()
    logger = MagicMock()

    responses_repo.get_response_by_id.side_effect = RuntimeError("DB error")

    result = retrieve_questionnaire_by_response(
        "res_123",
        responses_repo,
        questions_repo,
        logger
    )

    responses_repo.get_response_by_id.assert_called_once_with("res_123")
    logger.error.assert_called_once()

    questions_repo.get_questions_by_questionnaire_id.assert_not_called()

    assert result[0] is None
    assert result[1] is None

def test_retrieve_questionnaire_by_response_questions_repo_fail():
    responses_repo = MagicMock()
    questions_repo = MagicMock()
    logger = MagicMock()

    mock_response = MagicMock()
    mock_response.data = [
        {"questionnaires": {"id": "q_123"}}
    ]
    responses_repo.get_response_by_id.return_value = mock_response

    questions_repo.get_questions_by_questionnaire_id.side_effect = RuntimeError("DB error")

    result = retrieve_questionnaire_by_response(
        "res_123",
        responses_repo,
        questions_repo,
        logger
    )
        
    responses_repo.get_response_by_id.assert_called_once_with("res_123")
    questions_repo.get_questions_by_questionnaire_id.assert_called_once_with("q_123")
    logger.error.assert_called_once_with("Database error: DB error")

    assert result[0] is mock_response
    assert result[1] is None

def test_retrieve_response_info_response_repo_fail():
    responses_repo = MagicMock()
    answers_repo = MagicMock()
    logger = MagicMock()

    responses_repo.get_response_by_id.side_effect = RuntimeError("DB error")

    result = retrieve_response_info(
        "res_123",
        responses_repo,
        answers_repo,
        logger
    )

    responses_repo.get_response_by_id.assert_called_once_with("res_123")
    logger.error.assert_called_once()

    answers_repo.get_answers_by_response_id.assert_not_called()

    assert result[0] is None
    assert result[1] is None

def test_retrieve_response_info_answers_repo_fail():
    responses_repo = MagicMock()
    answers_repo = MagicMock()
    logger = MagicMock()

    mock_response = MagicMock()
    responses_repo.get_response_by_id.return_value = mock_response

    answers_repo.get_answers_by_response_id.side_effect = RuntimeError("DB error")

    result = retrieve_response_info(
        "res_123",
        responses_repo,
        answers_repo,
        logger
    )

    responses_repo.get_response_by_id.assert_called_once_with("res_123")
    answers_repo.get_answers_by_response_id.assert_called_once_with("res_123")
    logger.error.assert_called_once_with("Database error: DB error")

    assert result[0] is mock_response
    assert result[1] is None




        

