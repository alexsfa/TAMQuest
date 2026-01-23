import streamlit as st

from utils.generate_questionnaires import (
    generate_tam_questions,
    generate_additional_tam_questions,
)


def retrieve_questionnaire(
    questionnaire_id: str,
    questionnaires_repo,
    questions_repo,
    likert_scales_repo,
    likert_scale_options_repo,
    logger
):
    questionnaire_info = None
    questions_info = None
    likert_scale_info = None
    likert_scale_options = None

    questionnaire_info = None
    try:
        questionnaire_info = (
            questionnaires_repo.get_questionnaire_by_id(
                questionnaire_id
            )
        )
    except RuntimeError as e:
        logger.error(f"Database error: {e}")
        return [
            questionnaire_info,
            questions_info,
            likert_scale_info,
            likert_scale_options
        ]

    try:
        questions_info = (
            questions_repo.get_questions_by_questionnaire_id(
                questionnaire_id
            )
        )
    except RuntimeError as e:
        logger.error(f"Database error: {e}")
        return [
            questionnaire_info,
            questions_info,
            likert_scale_info,
            likert_scale_options
        ]

    try:
        likert_scale_info = (
            likert_scales_repo.get_likert_scale_by_questionnaire_id(
                questionnaire_id
            )
        )
    except RuntimeError as e:
        logger.error(f"Database error: {e}")
        return [
            questionnaire_info,
            questions_info,
            likert_scale_info,
            likert_scale_options
        ]

    try:
        likert_scale_options = (
            likert_scale_options_repo.get_options_by_likert_scale_id(
                likert_scale_info.data[0]["id"]
            )
        )
    except RuntimeError as e:
        logger.error(f"Database error: {e}")
        return [
            questionnaire_info,
            questions_info,
            likert_scale_info,
            likert_scale_options
        ]

    return [
        questionnaire_info,
        questions_info,
        likert_scale_info,
        likert_scale_options
    ]


"""
The retrieve_questionnaire_by_response functions gets the response by its id,
retrieving its corresponding questionnaire.
By response's corresponding questionnaire id, the function retrieves the
questionnaire's questions and likert scale
"""


def retrieve_questionnaire_by_response(
    response_id: str,
    responses_repo,
    questions_repo,
    likert_scales_repo,
    likert_scale_options_repo,
    logger
):
    response_info = None
    questions_info = None
    likert_scale_info = None
    likert_scale_options = None

    try:
        response_info = responses_repo.get_response_by_id(response_id)
    except RuntimeError as e:
        logger.error(f"Database error: {e}")
        return [
            response_info,
            questions_info,
            likert_scale_info,
            likert_scale_options
        ]

    try:
        questions_info = (
            questions_repo.get_questions_by_questionnaire_id(
                response_info.data[0]["questionnaires"]["id"]
            )
        )
    except RuntimeError as e:
        logger.error(f"Database error: {e}")
        return [
            response_info,
            questions_info,
            likert_scale_info,
            likert_scale_options
        ]

    try:
        likert_scale_info = (
            likert_scales_repo.get_likert_scale_by_questionnaire_id(
                response_info.data[0]["questionnaires"]["id"]
            )
        )
    except RuntimeError as e:
        logger.error(f"Database error: {e}")
        return [
            response_info,
            questions_info,
            likert_scale_info,
            likert_scale_options
        ]

    try:
        likert_scale_options = (
            likert_scale_options_repo.get_options_by_likert_scale_id(
                likert_scale_info.data[0]["id"]
            )
        )
    except RuntimeError as e:
        logger.error(f"Database error: {e}")
        return [
            response_info,
            questions_info,
            likert_scale_info,
            likert_scale_options
        ]

    return [
        response_info,
        questions_info,
        likert_scale_info,
        likert_scale_options
    ]


"""
The submit_questionnaire_likert_scale function submits
the likert scale of the questionnaire and its corresponding options.
"""


def submit_questionnaire_likert_scale(
    questionnaire_id: str,
    likert_scale_options: list,
    likert_scales_repo,
    likert_scale_options_repo,
    logger
):

    if len(likert_scale_options) == 0:
        raise ValueError("Failed to create the questionnaire's likert scale")

    q_likert_scale_info = None
    try:
        q_likert_scale_info = (
            likert_scales_repo.create_likert_scale(questionnaire_id)
        )
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    if q_likert_scale_info is not None:

        likert_scale_options_insert = []
        try:
            for position, label in enumerate(likert_scale_options):
                likert_scale_options_insert.append(
                    {
                        'likert_scale_id': q_likert_scale_info.data[0]["id"],
                        'value': position + 1,
                        'label': label
                    }
                )
            likert_scale_options_repo.create_likert_scale_options(
                likert_scale_options_insert
            )
        except RuntimeError as e:
            logger.error(f"Database error: {e}")

    return q_likert_scale_info


"""
The collect_likert_scale_options function returns a list
with the likert scale level labels that the admin has submitted.
"""


def collect_likert_scale_options():
    likert_scale_levels = []

    for i in range(st.session_state["questionnaire_likert_scale_levels"]):
        likert_scale_levels.append(st.session_state[f"likert_scale_lvl_{i+1}"])

    return likert_scale_levels


def submit_questionnaire(
    app_name: str,
    q_details: str,
    user_id: str,
    questionnaires_repo,
    questions_repo,
    likert_scales_repo,
    likert_scale_options_repo,
    logger,
    custom_questions: dict | None = None
):

    if app_name.strip() == "":
        st.warning("Please enter an app name.")
        return

    if q_details and q_details.strip():
        questionnaire_details = q_details.strip()
    else:
        questionnaire_details = None

    if custom_questions is None:
        custom_questions = {}

    questionnaire_likert_scale_options = collect_likert_scale_options()
    if not all(questionnaire_likert_scale_options):
        st.warning("Please enter values for all the likert scale levels")
        return

    questionnaire = None
    try:
        questionnaire = (
            questionnaires_repo.create_questionnaire(
                app_name,
                questionnaire_details,
                user_id
            )
        )
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    if questionnaire is not None:
        questions = generate_tam_questions(app_name)

        if (
                "add_questions" in st.session_state and
                st.session_state["add_questions"]
        ):
            questions.update(
                generate_additional_tam_questions(
                    app_name
                )
            )

        questions_to_insert = []
        position = 1

        for category, qs in questions.items():
            is_negative = (
                True
                if category in ["Computer Anxiety", "Risk", "Trust"]
                else False
            )
            for question_text in qs:
                questions_to_insert.append({
                    "questionnaire_id": questionnaire.data[0]["id"],
                    "question_text": question_text,
                    "position": position,
                    "category": category,
                    "is_custom": False,
                    "is_negative": is_negative
                })
                position += 1

            if category in custom_questions:
                for qs in custom_questions[category]:
                    question_text, negative_wording = qs
                    questions_to_insert.append({
                        "questionnaire_id": questionnaire.data[0]["id"],
                        "question_text": question_text,
                        "position": position,
                        "category": category,
                        "is_custom": True,
                        "is_negative": negative_wording
                    })
                    position += 1

        questions_insert = None
        try:
            questions_insert = (
                questions_repo.create_questions(questions_to_insert)
            )
        except RuntimeError as e:
            logger.error(f"Database error: {e}")

        likert_scale_insert = (
            submit_questionnaire_likert_scale(
                questionnaire.data[0]["id"],
                questionnaire_likert_scale_options,
                likert_scales_repo,
                likert_scale_options_repo,
                logger
            )
        )

        return [questionnaire, questions_insert, likert_scale_insert]
