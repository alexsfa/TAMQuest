import pytest
from unittest.mock import MagicMock, patch
import services.response_services as r_services

def mock_answers():
    answers = MagicMock()
    answers.data = [
        {"id": "a_1", "response_id": "res_123", "question_id": "q_1", "selected_option": "l_s_o_1"},
        {"id": "a_2", "response_id": "res_123", "question_id": "q_2", "selected_option": "l_s_o_2"},
        {"id": "a_3", "response_id": "res_123", "question_id": "q_3", "selected_option": "l_s_o_3"},
    ]
    return answers

def mock_questions():
    questions = MagicMock()
    questions.data = [
        {"id": "q1"},
        {"id": "q2"} 
    ]
    return questions

def mock_likert_scale_options():
    likert_scale_options = MagicMock()
    likert_scale_options.data = [
        {"id": "opt1", "label": "Agree"},
        {"id": "opt2", "label": "Disagree"}
    ]
    return likert_scale_options

def test_retrieve_response_info():
    responses_repo = MagicMock()
    answers_repo = MagicMock()
    logger = MagicMock()

    response_data = MagicMock()
    response_data.data = [{"id": "res_123"}]
    answers_data = mock_answers()

    responses_repo.get_response_by_id.return_value = response_data
    answers_repo.get_answers_by_response_id.return_value = answers_data

    result = r_services.retrieve_response_info(
        "res_123",
        responses_repo,
        answers_repo,
        logger 
    )

    responses_repo.get_response_by_id.assert_called_once_with("res_123")
    answers_repo.get_answers_by_response_id.assert_called_once_with("res_123")
    logger.error.assert_not_called()

    assert result == [response_data, answers_data]

def test_submit_response():

    with patch("services.response_services.st") as mock_st, \
         patch("services.response_services.responses_repo") as mock_responses_repo, \
         patch("services.response_services.answers_repo") as mock_answers_repo:

        mock_st.session_state = {
            "user_id": "u1",
            "q1_answer": "Agree",
            "q2_answer": "Disagree"
        }
        mock_st.error = MagicMock()

        mock_responses_repo.get_responses_by_questionnaire_id.return_value = MagicMock(
            data=[{"id": "r1"}]
        )

        mock_answers_repo.update_answers.return_value = "answers_updated"
        mock_responses_repo.update_response_on_submitted.return_value = "response_submitted"

        result = r_services.submit_response(
            "u1",
            "q123",
            get_submitted=True,
            questions=mock_questions(),
            likert_scale_options=mock_likert_scale_options()
        )

        mock_responses_repo.update_response_on_submitted.assert_called_once()
        assert result == ["response_submitted", "answers_updated"]

def test_retrieve_response_info_response_repo_fail():
    responses_repo = MagicMock()
    answers_repo = MagicMock()
    logger = MagicMock()

    responses_repo.get_response_by_id.side_effect = RuntimeError("DB error")

    result = r_services.retrieve_response_info(
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

    result = r_services.retrieve_response_info(
        "res_123",
        responses_repo,
        answers_repo,
        logger 
    )

    responses_repo.get_response_by_id.assert_called_once_with("res_123")
    answers_repo.get_answers_by_response_id.assert_called_once_with("res_123")

    logger.error.assert_called_once()

    assert result[0] is mock_response
    assert result[1] is None

def test_submit_response_not_all_answered():

    with patch("services.response_services.st") as mock_st:
        mock_st.session_state = {
            "q1_answer": "Agree",
            "q2_answer": None
        }

        mock_st.error = MagicMock()

        result = r_services.submit_response(
            user_id="u1",
            questionnaire_id="q123",
            get_submitted=True,
            questions=mock_questions(),
            likert_scale_options=mock_likert_scale_options()
        )

        mock_st.error.assert_called_once_with(
            "Please answer all of the questions before submitting"
        )

        assert result is None

def test_submit_response_create_new_response():
    mock_questions = MagicMock()
    mock_questions.data = [
        {"id": "q1"},
        {"id": "q2"} 
    ]
    mock_likert_scale_options = MagicMock()
    mock_likert_scale_options.data = [
        {"id": "opt1", "label": "Agree"},
        {"id": "opt2", "label": "Disagree"}
    ]

    with patch("services.response_services.st") as mock_st, \
        patch("services.response_services.responses_repo") as mock_responses_repo, \
        patch("services.response_services.answers_repo") as mock_answers_repo: 

        mock_st.session_state = {
            "user_id": "u1",
            "q1_answer": "Agree",
            "q2_answer": "Disagree"
        }
        mock_st.error = MagicMock()

        mock_responses_repo.get_responses_by_questionnaire_id.return_value = MagicMock(data=[])

        response_insert = MagicMock()
        response_insert.data = [{"id": "r1"}]
        mock_responses_repo.create_response.return_value = response_insert

        mock_answers_repo.create_answers.return_value = "answers_inserted"

        result = r_services.submit_response(
            "u1",
            "q123",
            get_submitted=False,
            questions=mock_questions(),
            likert_scale_options=mock_likert_scale_options()
        )

        mock_responses_repo.create_response.assert_called_once()
        mock_answers_repo.create_answers.assert_called_once()

        assert result == [response_insert, "answers_inserted"]

def test_submit_response_update_draft():

    with patch("services.response_services.st") as mock_st, \
        patch("services.response_services.responses_repo") as mock_responses_repo, \
        patch("services.response_services.answers_repo") as mock_answers_repo:

        mock_st.session_state = {
            "user_id": "u1",
            "q1_answer": "Agree",
            "q2_answer": "Disagree"
        }
        mock_st.error = MagicMock()

        # Existing draft
        mock_responses_repo.get_responses_by_questionnaire_id.return_value = MagicMock(
            data=[{"id": "r1"}]
        )

        mock_answers_repo.update_answers.return_value = "answers_updated"

        result = r_services.submit_response(
            "u1",
            "q123",
            get_submitted=False,
            questions=mock_questions(),
            likert_scale_options=mock_likert_scale_options()
        )

        mock_answers_repo.update_answers.assert_called_once()
        assert result[1] == "answers_updated"


 

