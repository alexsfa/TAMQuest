import streamlit as st
import re
from datetime import datetime

from database.questionnaires import Questionnaires
from database.questions import Questions
from database.responses import Responses
from database.answers import Answers

from services.response_services import  submit_response
from services.questionnaire_services import retrieve_questionnaire, retrieve_questionnaire_by_response

from utils import supabase_client 
from utils.menu import menu
from utils.logger_config import logger
from utils.components import format_time, set_response_ui

client = supabase_client.get_client()
questionnaires_repo = Questionnaires(client)
questions_repo = Questions(client)
responses_repo = Responses(client)
answers_repo = Answers(client)

if __name__ == "__main__":
    
    menu(client)
    
    current_questionnaire = None
    if st.session_state.edit_response_mode == True:
        current_questionnaire = retrieve_questionnaire_by_response(st.session_state["current_response_id"], responses_repo, questions_repo, logger)
        questionnaire_id = current_questionnaire[0].data[0]["questionnaires"]["id"]
        questionnaire_title = current_questionnaire[0].data[0]["questionnaires"]["title"]
        questionnaire_details = current_questionnaire[0].data[0]["questionnaires"]["details"]
        questionnaire_timestamp = current_questionnaire[0].data[0]["questionnaires"]["created_at"]
    else:
        current_questionnaire = retrieve_questionnaire(st.session_state["current_questionnaire_id"], questionnaires_repo, 
        questions_repo, logger)
        questionnaire_id = current_questionnaire[0].data[0]["id"]
        questionnaire_title = current_questionnaire[0].data[0]["title"]
        questionnaire_details = current_questionnaire[0].data[0]["details"]
        questionnaire_timestamp = current_questionnaire[0].data[0]["created_at"]

    if current_questionnaire[0] is None:
        st.error("Error during the questionnaire's retrieval")
        st.stop()

    st.title(questionnaire_title)

    if questionnaire_details == "": 
        st.write("No further details were provided")
    else: 
        st.write(questionnaire_details)

    formatted_time = format_time(questionnaire_timestamp)
    st.write(formatted_time)

    questions = current_questionnaire[1]
    
    response_draft_info = None
    try:
        response_draft_info = responses_repo.get_responses_by_questionnaire_id(st.session_state["user_id"], questionnaire_id, False)
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    if response_draft_info is None:
        st.error("Error during draft search! Please try again later")
        st.stop()
    elif len(response_draft_info.data) == 0:
        set_response_ui(questions)
    else:
        draft_answers = None
        try:
            draft_answers = answers_repo.get_answers_by_response_id(response_draft_info.data[0]["id"])
        except RuntimeError as e:
            logger.error(f"Database errore: {e}")

        if draft_answers is None:
            st.error("Error during draft answers retrieval!")
            st.stop()
        elif len(draft_answers.data) == 0:
            set_response_ui(questions)
        else:
            set_response_ui(questions, draft_answers)
    
    message_box = st.empty()
    col1, col2 = st.columns([1,1])

    with col1:
        if st.button("Submit"):
            submission_state = submit_response(st.session_state["user_id"], questionnaire_id, True, questions)
            if submission_state is None:
                message_box.error("Error during your response's submission")
            else:
                message_box.success("Your response has been submitted")

    with col2:
        if st.button("Save Draft"):
            submission_state = submit_response(st.session_state["user_id"], questionnaire_id, False, questions)
            if submission_state is None:
                message_box.error("Error during your draft's submission")
            else:
                message_box.success("Your draft has been submitted")
    

    



