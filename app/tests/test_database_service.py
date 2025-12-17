import pytest
from unittest.mock import MagicMock
from services.database_service import retrieve_questionnaire, retrieve_questionnaire_by_response

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


def test_retrieve_questionnaire_fail():
    questionnaires_repo = MagicMock()
    questions_repo = MagicMock()
    logger = MagicMock()

    questionnaires_repo.get_questionnaire_by_id.side_effect = RuntimeError("DB error")
    questions_repo.get_questions_by_questionnaire_id.return_value = {"data": []}

    result = retrieve_questionnaire(
        "q_123",
        questionnaires_repo,
        questions_repo,
        logger
    )

    questionnaires_repo.get_questionnaire_by_id.assert_called_once_with("q_123")
    questions_repo.get_questions_by_questionnaire_id.assert_called_once_with("q_123")
    logger.error.assert_called_once()

    assert result[0] is None
    assert result[1] == {"data": []}

def test_retrieve_questionnaire_by_response_fail():
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

        

