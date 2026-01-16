import pytest
from unittest.mock import MagicMock, patch
import services.questionnaire_services as q_services

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

    result = q_services.retrieve_questionnaire(
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

    result = q_services.retrieve_questionnaire_by_response(
        "res_123",
        responses_repo,
        questions_repo,
        likert_scales_repo,
        likert_scale_options_repo,
        logger
    )

    responses_repo.get_response_by_id.assert_called_once_with("res_123")
    questions_repo.get_questions_by_questionnaire_id.assert_called_once_with("q_123")
    likert_scales_repo.get_likert_scale_by_questionnaire_id.assert_called_once_with("q_123")
    likert_scale_options_repo.get_options_by_likert_scale_id.assert_called_once_with("l_s_123")
    logger.error.assert_not_called()

    assert result == [response_data, questions_data, likert_scale_data, likert_scale_options_data]

def test_submit_questionnaire_likert_scale():
    likert_scales_repo = MagicMock()
    likert_scale_options_repo = MagicMock()
    logger = MagicMock()

    mock_likert_scale = MagicMock()
    mock_likert_scale.data = [{"id": "l_s_123"}]  
    likert_scales_repo.create_likert_scale.return_value = mock_likert_scale

    result = q_services.submit_questionnaire_likert_scale(
        "q_123",
        ["Disagree", "Neutral", "Agree"],
        likert_scales_repo,
        likert_scale_options_repo,
        logger
    )

    likert_scales_repo.create_likert_scale.assert_called_once_with("q_123")

    likert_scale_options_repo.create_likert_scale_options.assert_called_once_with([
        {"likert_scale_id": "l_s_123", "value": 1, "label": "Disagree"},
        {"likert_scale_id": "l_s_123", "value": 2, "label": "Neutral"},
        {"likert_scale_id": "l_s_123", "value": 3, "label": "Agree"},
    ])

    logger.error.assert_not_called()
    assert result is mock_likert_scale

def test_submit_questionnaire():
    questionnaires_repo = MagicMock()
    questions_repo = MagicMock()
    likert_scales_repo = MagicMock()
    likert_scale_options_repo = MagicMock()
    logger = MagicMock()

    mock_questionnaire = MagicMock()
    mock_questionnaire.data = [{"id": "q_123"}]
    questionnaires_repo.create_questionnaire.return_value = mock_questionnaire
    questions_repo.create_questions.return_value = "mock_questions"
    mock_likert_scale = MagicMock()
    likert_scale_options = ["Disagree", "Neutral", "Agree"]

    with patch("services.questionnaire_services.collect_likert_scale_options", return_value=likert_scale_options), \
        patch("services.questionnaire_services.generate_tam_questions", return_value={
            "Perceived Usefulness": ["Question 1", "Question 2"]
        }), \
        patch("services.questionnaire_services.generate_additional_tam_questions", return_value={}), \
        patch("services.questionnaire_services.submit_questionnaire_likert_scale", return_value=mock_likert_scale), \
        patch("services.questionnaire_services.st") as mock_st:

        mock_st.session_state = {}

        result = q_services.submit_questionnaire(
            app_name="Test App",
            q_details="Test details",
            user_id="user_123",
            questionnaires_repo=questionnaires_repo,
            questions_repo=questions_repo,
            likert_scales_repo=likert_scales_repo,
            likert_scale_options_repo=likert_scale_options_repo,
            logger=logger
        )

    questionnaires_repo.create_questionnaire.assert_called_once_with("Test App", "Test details", "user_123")
    questions_repo.create_questions.assert_called_once()
    q_services.submit_questionnaire_likert_scale(
        "q_123", likert_scale_options, likert_scales_repo, likert_scale_options_repo, logger
    )

    assert result == [mock_questionnaire, "mock_questions", mock_likert_scale]

    mock_st.warning.assert_not_called()

def test_retrieve_questionnaire_repo_fail():
    questionnaires_repo = MagicMock()
    questions_repo = MagicMock()
    likert_scales_repo = MagicMock()
    likert_scale_options_repo = MagicMock()
    logger = MagicMock()

    questionnaires_repo.get_questionnaire_by_id.side_effect = RuntimeError("DB error")

    result = q_services.retrieve_questionnaire(
        "q_123",
        questionnaires_repo,
        questions_repo,
        likert_scales_repo,
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
    likert_scales_repo = MagicMock()
    likert_scale_options_repo = MagicMock()
    logger = MagicMock()

    mock_questionnaire = MagicMock()
    questionnaires_repo.get_questionnaire_by_id.return_value = mock_questionnaire

    questions_repo.get_questions_by_questionnaire_id.side_effect = RuntimeError("DB error")

    result = q_services.retrieve_questionnaire(
        "q_123",
        questionnaires_repo,
        questions_repo,
        likert_scales_repo,
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

def test_retrieve_questionnaire_likert_scales_repo_fail():
    questionnaires_repo = MagicMock()
    questions_repo = MagicMock()
    likert_scales_repo = MagicMock()
    likert_scale_options_repo = MagicMock()
    logger = MagicMock()

    mock_questionnaire = MagicMock()
    mock_questions = MagicMock()
    questionnaires_repo.get_questionnaire_by_id.return_value = mock_questionnaire
    questions_repo.get_questions_by_questionnaire_id.return_value = mock_questions

    likert_scales_repo.get_likert_scale_by_questionnaire_id.side_effect = RuntimeError("DB error")

    result = q_services.retrieve_questionnaire(
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

    logger.error.assert_called_once_with("Database error: DB error")

    assert result[0] is mock_questionnaire
    assert result[1] is mock_questions
    assert result[2] is None
    assert result[3] is None

def test_retrieve_questionnaire_likert_scale_options_repo_fail():
    questionnaires_repo = MagicMock()
    questions_repo = MagicMock()
    likert_scales_repo = MagicMock()
    likert_scale_options_repo = MagicMock()
    logger = MagicMock()

    mock_questionnaire = MagicMock()
    mock_questions = MagicMock()
    mock_likert_scale = MagicMock()
    mock_likert_scale.data = [{"id": "l_s_123"}]
    questionnaires_repo.get_questionnaire_by_id.return_value = mock_questionnaire
    questions_repo.get_questions_by_questionnaire_id.return_value = mock_questions
    likert_scales_repo.get_likert_scale_by_questionnaire_id.return_value = mock_likert_scale

    likert_scale_options_repo.get_options_by_likert_scale_id.side_effect = RuntimeError("DB error")

    result = q_services.retrieve_questionnaire(
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

    logger.error.assert_called_once_with("Database error: DB error")

    assert result[0] is mock_questionnaire
    assert result[1] is mock_questions
    assert result[2] is mock_likert_scale
    assert result[3] is None

def test_retrieve_questionnaire_by_response_repo_fail():
    responses_repo = MagicMock()
    questions_repo = MagicMock()
    likert_scales_repo = MagicMock()
    likert_scales_options_repo = MagicMock()
    logger = MagicMock()

    responses_repo.get_response_by_id.side_effect = RuntimeError("DB error")

    result = q_services.retrieve_questionnaire_by_response(
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

    result = q_services.retrieve_questionnaire_by_response(
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

def test_retrieve_questionnaire_by_response_likert_scales_repo_fail():
    responses_repo = MagicMock()
    questions_repo = MagicMock()
    likert_scales_repo = MagicMock()
    likert_scale_options_repo = MagicMock()
    logger = MagicMock()

    mock_response = MagicMock()
    mock_response.data = [
        {"questionnaires": {"id": "q_123"}}
    ]
    mock_questions = MagicMock()
    responses_repo.get_response_by_id.return_value = mock_response
    questions_repo.get_questions_by_questionnaire_id.return_value = mock_questions

    likert_scales_repo.get_likert_scale_by_questionnaire_id.side_effect = RuntimeError("DB error")

    result = q_services.retrieve_questionnaire_by_response(
        "res_123",
        responses_repo,
        questions_repo,
        likert_scales_repo,
        likert_scale_options_repo,
        logger
    )
        
    responses_repo.get_response_by_id.assert_called_once_with("res_123")
    questions_repo.get_questions_by_questionnaire_id.assert_called_once_with("q_123")
    likert_scales_repo.get_likert_scale_by_questionnaire_id.assert_called_once_with("q_123")
    logger.error.assert_called_once_with("Database error: DB error")

    assert result[0] is mock_response
    assert result[1] is mock_questions
    assert result[2] is None
    assert result[3] is None

def test_retrieve_questionnaire_by_response_likert_scale_options_repo_fail():
    responses_repo = MagicMock()
    questions_repo = MagicMock()
    likert_scales_repo = MagicMock()
    likert_scale_options_repo = MagicMock()
    logger = MagicMock()

    mock_response = MagicMock()
    mock_response.data = [
        {"questionnaires": {"id": "q_123"}}
    ]
    mock_questions = MagicMock()
    mock_likert_scale = MagicMock()
    mock_likert_scale.data = [
        {"id": "l_s_123"}
    ]
    responses_repo.get_response_by_id.return_value = mock_response
    questions_repo.get_questions_by_questionnaire_id.return_value = mock_questions
    likert_scales_repo.get_likert_scale_by_questionnaire_id.return_value = mock_likert_scale

    likert_scale_options_repo.get_options_by_likert_scale_id.side_effect = RuntimeError("DB error")

    result = q_services.retrieve_questionnaire_by_response(
        "res_123",
        responses_repo,
        questions_repo,
        likert_scales_repo,
        likert_scale_options_repo,
        logger
    )
        
    responses_repo.get_response_by_id.assert_called_once_with("res_123")
    questions_repo.get_questions_by_questionnaire_id.assert_called_once_with("q_123")
    likert_scales_repo.get_likert_scale_by_questionnaire_id.assert_called_once_with("q_123")
    likert_scale_options_repo.get_options_by_likert_scale_id.assert_called_once_with("l_s_123")
    logger.error.assert_called_once_with("Database error: DB error")

    assert result[0] is mock_response
    assert result[1] is mock_questions
    assert result[2] is mock_likert_scale
    assert result[3] is None

def test_submit_questionnaire_likert_scale_repo_fail():
    likert_scales_repo = MagicMock()
    likert_scale_options_repo = MagicMock()
    logger = MagicMock()

    likert_scales_repo.create_likert_scale.side_effect = RuntimeError("DB error")

    result = q_services.submit_questionnaire_likert_scale(
        "q_123",
        ["Disagree","Agree"],
        likert_scales_repo,
        likert_scale_options_repo,
        logger
    )

    likert_scales_repo.create_likert_scale.assert_called_once_with("q_123")
    likert_scale_options_repo.create_likert_scale_options.assert_not_called()
    logger.error.assert_called_once_with("Database error: DB error")

    assert result is None

def test_submit_questionnaire_likert_scale_options_repo_fail():
    likert_scales_repo = MagicMock()
    likert_scale_options_repo = MagicMock()
    logger = MagicMock()

    mock_likert_scale = MagicMock()
    mock_likert_scale.data = [{"id": "l_s_123"}]

    likert_scales_repo.create_likert_scale.return_value = mock_likert_scale
    likert_scale_options_repo.create_likert_scale_options.side_effect = RuntimeError("DB error")

    result = q_services.submit_questionnaire_likert_scale(
        "q_123",
        ["Strongly Disagree"],
        likert_scales_repo,
        likert_scale_options_repo,
        logger
    )


    likert_scale_options_repo.create_likert_scale_options.assert_called_once()
    logger.error.assert_called_once_with("Database error: DB error")

    assert result is mock_likert_scale

def test_submit_questionnaire_likert_scale_empty_options():
    likert_scales_repo = MagicMock()
    likert_scale_options_repo = MagicMock()
    logger = MagicMock()

    with pytest.raises(ValueError) as exc_info:
        q_services.submit_questionnaire_likert_scale(
            "q_123",
            [],
            likert_scales_repo,
            likert_scale_options_repo,
            logger
        )

    assert str(exc_info.value) == "Failed to create the questionnaire's likert scale"

    likert_scales_repo.create_likert_scale.assert_not_called()
    likert_scale_options_repo.create_likert_scale_options.assert_not_called()

    logger.error.assert_not_called()

def test_submit_questionnaire_empty_app_name():
    with patch("services.questionnaire_services.st") as mock_st:
        mock_st.warning = MagicMock()
        result = q_services.submit_questionnaire(
            app_name="   ",
            q_details="details",
            user_id="user_123",
            questionnaires_repo=MagicMock(),
            questions_repo=MagicMock(),
            likert_scales_repo=MagicMock(),
            likert_scale_options_repo=MagicMock(),
            logger=MagicMock()
        )

        assert result is None
        mock_st.warning.assert_called_once_with("Please enter an app name.")

def test_submit_questionnaire_empty_likert_options():
    with patch("services.questionnaire_services.collect_likert_scale_options", return_value=[None, "Agree"]), \
         patch("services.questionnaire_services.st") as mock_st:
        mock_st.warning = MagicMock()
        result = q_services.submit_questionnaire(
            app_name="Test App",
            q_details="details",
            user_id="user_123",
            questionnaires_repo=MagicMock(),
            questions_repo=MagicMock(),
            likert_scales_repo=MagicMock(),
            likert_scale_options_repo=MagicMock(),
            logger=MagicMock()
        )
        assert result is None
        mock_st.warning.assert_called_once_with("Please enter values for all the likert scale levels")

def test_submit_questionnaire_questionnaire_repo_fail():
    questionnaires_repo = MagicMock()
    questions_repo = MagicMock()
    likert_scales_repo = MagicMock()
    likert_scale_options_repo = MagicMock()
    logger = MagicMock()

    questionnaires_repo.create_questionnaire.side_effect = RuntimeError("DB error")

    with patch("services.questionnaire_services.collect_likert_scale_options", return_value=["Disagree", "Agree"]), \
        patch("services.questionnaire_services.st") as mock_st:

        mock_st.session_state = {}

        result = q_services.submit_questionnaire(
            "Test App",
            "details",
            "user_123",
            questionnaires_repo,
            questions_repo,
            likert_scales_repo,
            likert_scale_options_repo,
            logger
        )

    logger.error.assert_called_once_with("Database error: DB error")
    questions_repo.create_questions.assert_not_called()

    assert result is None

def test_submit_questionnaire_questions_repo_fail():
    questionnaires_repo = MagicMock()
    questions_repo = MagicMock()
    likert_scales_repo = MagicMock()
    likert_scale_options_repo = MagicMock()
    logger = MagicMock()

    mock_questionnaire = MagicMock()
    mock_questionnaire.data = [{"id": "q_123"}]
    questionnaires_repo.create_questionnaire.return_value = mock_questionnaire

    questions_repo.create_questions.side_effect = RuntimeError("DB error")

    with patch("services.questionnaire_services.collect_likert_scale_options", return_value=["Disagree", "Agree"]), \
         patch("services.questionnaire_services.generate_tam_questions", return_value={}), \
         patch("services.questionnaire_services.submit_questionnaire_likert_scale") as mock_submit_ls, \
         patch("services.questionnaire_services.st") as mock_st:

        mock_st.session_state = {}

        result = q_services.submit_questionnaire(
            "Test App",
            "details",
            "user_123",
            questionnaires_repo,
            questions_repo,
            likert_scales_repo,
            likert_scale_options_repo,
            logger
        )

    logger.error.assert_called_once()
    mock_submit_ls.assert_called_once()

    assert result[0] is mock_questionnaire
    assert result[1] is None
