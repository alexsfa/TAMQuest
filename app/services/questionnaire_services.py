import streamlit as st

from database.questionnaires import Questionnaires
from database.questions import Questions
from database.responses import Responses
from database.likert_scales import Likert_scales
from database.likert_scale_options import Likert_scale_options

from utils.generate_questionnaires import generate_tam_questions, generate_additional_tam_questions,ESSENTIAL_TAM_QUESTIONS, ADDITIONAL_TAM_QUESTIONS
from utils import supabase_client 
from utils.logger_config import logger

client = supabase_client.get_client()
questionnaires_repo = Questionnaires(client)
questions_repo = Questions(client)
responses_repo = Responses(client)
likert_scales_repo = Likert_scales(client)
likert_scale_options_repo = Likert_scale_options(client)




def retrieve_questionnaire(questionnaire_id: str, questionnaires_repo, questions_repo, logger):

    questionnaire_info = None
    try:
        questionnaire_info = questionnaires_repo.get_questionnaire_by_id(questionnaire_id)
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    questions_info = None
    try:
        if questionnaire_info is not None:
            questions_info = questions_repo.get_questions_by_questionnaire_id(questionnaire_id)
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    return [questionnaire_info, questions_info]


def retrieve_questionnaire_by_response(response_id: str, responses_repo, questions_repo, logger):

    response_info = None
    try:
        response_info = responses_repo.get_response_by_id(response_id)
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    questions_info = None
    try:
        if response_info is not None:
            questions_info = questions_repo.get_questions_by_questionnaire_id(response_info.data[0]["questionnaires"]["id"])
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    return [response_info, questions_info]

def submit_questionnaire_likert_scale(questionnaire_id:str, likert_scale_options:list):

    q_likert_scale_info = None
    try:
        q_likert_scale_info = likert_scales_repo.create_likert_scale(questionnaire_id)
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    if q_likert_scale_info is not None:

        likert_scale_options_info = None
        try:
            likert_scale_options_info = likert_scale_options_repo.create_likert_scale_options()
        except RuntimeError as e:
            logger.error(f"Database error: {e}")


    return q_likert_scale_info

def submit_questionnaire( app_name: str, q_details: str, user_id: str, questionnaires_repo, questions_repo, logger, custom_questions:dict | None=None):

    if app_name.strip() == "":
        st.warning("Please enter an app name.")
        return

    if q_details and q_details.strip():
        questionnaire_details = q_details.strip()
    else:
        questionnaire_details = None

    questionnaire = None
    try:
        questionnaire = questionnaires_repo.create_questionnaire(app_name, q_details, user_id)
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    if questionnaire is not None:
        questions = generate_tam_questions(ESSENTIAL_TAM_QUESTIONS, app_name)

        if "add_questions" in st.session_state and st.session_state["add_questions"]:
            questions.update(generate_additional_tam_questions(ADDITIONAL_TAM_QUESTIONS, app_name))

        for category, question in custom_questions.items():
            if category in questions.keys():
                for q in question:
                    questions[category].append(q)

        questions_to_insert = []
        position = 1

        for category, qs in questions.items():
            for question_text in qs:
                questions_to_insert.append({
                    "questionnaire_id": questionnaire.data[0]["id"],
                    "question_text": question_text,
                    "position": position,
                    "category": category
                })
                position += 1

        questions_insert = None
        try:   
            questions_insert = questions_repo.create_questions(questions_to_insert)
        except RuntimeError as e:
            logger.error("Database error: {e}")

        likert_scale_insert = submit_questionnaire_likert_scale(questionnaire.data[0]["id"])

        return [questionnaire, questions_insert, likert_scale_insert]