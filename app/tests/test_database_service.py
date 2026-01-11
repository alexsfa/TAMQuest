import pytest
from unittest.mock import MagicMock
from services.questionnaire_services import retrieve_questionnaire, retrieve_questionnaire_by_response, submit_questionnaire

@pytest.fixture
def mock_streamlit(monkeypatch):
    fake_st = MagicMock()
    fake_st.session_state = {
        "app_name": "TestApp",
        "q_details": "Some details",
        "add_questions": False
    }

    monkeypatch.setattr("services.questionnaire_services.st", fake_st)
    return fake_st

@pytest.fixture
def mock_question_generators(monkeypatch):
    monkeypatch.setattr(
        "services.questionnaire_services.generate_tam_questions",
        lambda questions, app_name: {
            "Perceived Usefulleness": ["Question 1", "Question 2"]
        }
    )

    monkeypatch.setattr(
        "services.questionnaire_services.generate_additional_tam_questions",
        lambda questions, app_name: {}
    )

def test_retrieve_questionnaire():
    questionnaires_repo = MagicMock()
    questions_repo = MagicMock()
    likert_scales_repo = MagicMock()
    likert_scale_options_repo = MagicMock()
    logger = MagicMock()

    questionnaire_data = {"id": "q_123", "title": "Test Questionnaire","details": "description", "created_by": "user_123", "created_at": "2025-12-15 14:03:34.15619+00"}
    questions_data = {"data": [{"id": "1", "questionnnaire_id": "q_123", "question_text": "Question 1", "position": 1}]}
    likert_scale_data = MagicMock()
    likert_scale_data.data = [{"id": "l_s_123"}]
    likert_scale_options_data = {"data": [{"id": "lso_1", "likert_scale_id": "l_s_123", "value": 1, "label": "Strongly Disagree"}]}

    questionnaires_repo.get_questionnaire_by_id.return_value = questionnaire_data
    questions_repo.get_questions_by_questionnaire_id.return_value = questions_data
    likert_scales_repo.get_likert_scale_by_questionnaire_id.return_value = likert_scale_data
    likert_scale_options_repo.get_options_by_likert_scale_id.return_value = likert_scale_options_data

    result = retrieve_questionnaire(
        "q_123",
        questionnaires_repo,
        questions_repo,
        likert_scales_repo,
        likert_scale_options_repo,
        logger
    )

    questionnaires_repo.get_questionnaire_by_id.assert_called_once_with("q_123")
    questions_repo.get_questions_by_questionnaire_id.assert_called_once_with("q_123")
    likert_scales_repo.get_likert_scale_by_questionnaire_id.assert_called_once_with("q_123")
    likert_scale_options_repo.get_options_by_likert_scale_id.assert_called_once_with("l_s_123")
    logger.error.assert_not_called()

    assert result == [questionnaire_data, questions_data, likert_scale_data, likert_scale_options_data]

def test_retrieve_questionnaire_by_response():
    responses_repo = MagicMock()
    questions_repo = MagicMock()
    likert_scales_repo = MagicMock()
    likert_scale_options_repo = MagicMock()
    logger = MagicMock()

    response_data = MagicMock()
    response_data.data = [{"questionnaires": {"id": "q_123"}}]
    questions_data = {"data": [{"id": "1", "questionnaire_id": "q_123", "question_text": "Question 1", "Category": "Perceived Usefulness"}]}
    likert_scale_data = MagicMock()
    likert_scale_data.data = [{"id": "l_s_123"}]
    likert_scale_options_data = {"data": [{"id": "lso_1", "likert_scale_id": "l_s_123", "value": 1, "label": "Strongly Disagree"}]}


    responses_repo.get_response_by_id.return_value = response_data
    questions_repo.get_questions_by_questionnaire_id.return_value = questions_data
    likert_scales_repo.get_likert_scale_by_questionnaire_id.return_value = likert_scale_data
    likert_scale_options_repo.get_options_by_likert_scale_id.return_value = likert_scale_options_data

    result = retrieve_questionnaire_by_response(
        "res_123",
        responses_repo,
        questions_repo,
        likert_scales_repo,
        likert_scale_options_repo,
        logger
    )

    responses_repo.get_response_by_id.assert_called_once_with("res_123")
    questions_repo.get_questions_by_questionnaire_id.assert_called_once_with(response_data.data[0]["questionnaires"]["id"])
    likert_scales_repo.get_likert_scale_by_questionnaire_id.return_value = likert_scale_data
    likert_scale_options_repo.get_options_by_likert_scale_id.return_value = likert_scale_options_data
    logger.error.assert_not_called()

    assert result == [response_data, questions_data, likert_scale_data, likert_scale_options_data]


def test_retrieve_questionnaire_repo_fail():
    questionnaires_repo = MagicMock()
    questions_repo = MagicMock()
    likert_scale_repo = MagicMock()
    likert_scale_options_repo = MagicMock()
    logger = MagicMock()

    questionnaires_repo.get_questionnaire_by_id.side_effect = RuntimeError("DB error")

    result = retrieve_questionnaire(
        "q_123",
        questionnaires_repo,
        questions_repo,
        likert_scale_repo,
        likert_scale_options_repo,
        logger,

    )

    questionnaires_repo.get_questionnaire_by_id.assert_called_once_with("q_123")
    logger.error.assert_called_once()

    questions_repo.get_questions_by_questionnaire_id.assert_not_called()

    assert result[0] is None
    assert result[1] is None
    assert result[2] is None
    assert result[3] is None

def test_retrieve_questionnaire_questions_repo_fail():
    questionnaires_repo = MagicMock()
    questions_repo = MagicMock()
    likert_scale_repo = MagicMock()
    likert_scale_options_repo = MagicMock()
    logger = MagicMock()

    mock_questionnaire = MagicMock()
    questionnaires_repo.get_questionnaire_by_id.return_value = mock_questionnaire

    questions_repo.get_questions_by_questionnaire_id.side_effect = RuntimeError("DB error")

    result = retrieve_questionnaire(
        "q_123",
        questionnaires_repo,
        questions_repo,
        likert_scale_repo,
        likert_scale_options_repo,
        logger
    )

    questionnaires_repo.get_questionnaire_by_id.assert_called_once_with("q_123")
    questions_repo.get_questions_by_questionnaire_id.assert_called_once_with("q_123")

    logger.error.assert_called_once_with("Database error: DB error")

    assert result[0] is mock_questionnaire
    assert result[1] is None
    assert result[2] is None
    assert result[3] is None

def test_retrieve_questionnaire_by_response_repo_fail():
    responses_repo = MagicMock()
    questions_repo = MagicMock()
    likert_scales_repo = MagicMock()
    likert_scales_options_repo = MagicMock()
    logger = MagicMock()

    responses_repo.get_response_by_id.side_effect = RuntimeError("DB error")

    result = retrieve_questionnaire_by_response(
        "res_123",
        responses_repo,
        questions_repo,
        likert_scales_repo,
        likert_scales_options_repo,
        logger
    )

    responses_repo.get_response_by_id.assert_called_once_with("res_123")
    logger.error.assert_called_once()

    questions_repo.get_questions_by_questionnaire_id.assert_not_called()

    assert result[0] is None
    assert result[1] is None
    assert result[2] is None
    assert result[3] is None

def test_retrieve_questionnaire_by_response_questions_repo_fail():
    responses_repo = MagicMock()
    questions_repo = MagicMock()
    likert_scales_repo = MagicMock()
    likert_scales_options_repo = MagicMock()
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
        likert_scales_repo,
        likert_scales_options_repo,
        logger
    )
        
    responses_repo.get_response_by_id.assert_called_once_with("res_123")
    questions_repo.get_questions_by_questionnaire_id.assert_called_once_with("q_123")
    logger.error.assert_called_once_with("Database error: DB error")

    assert result[0] is mock_response
    assert result[1] is None
    assert result[2] is None
    assert result[3] is None






        

