import streamlit as st

from database.responses import Responses
from database.answers import Answers

from database.responses import Responses
from database.answers import Answers

from utils import supabase_client 
from utils.logger_config import logger

client = supabase_client.get_client()
responses_repo = Responses(client)
answers_repo = Answers(client)

'''
The retrieve_response_info function retrieves a response by id and its corresponding answers
'''
def retrieve_response_info(response_id: str, responses_repo, answers_repo, logger):
    
    response = None
    try:
        response = responses_repo.get_response_by_id(response_id)
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    answers = None
    try:
        if response is not None:
            answers = answers_repo.get_answers_by_response_id(response_id)
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    return [response, answers]

def submit_response(user_id: str,questionnaire_id: str, get_submitted: bool, questions):

    # checking if all the questions have been answered
    all_answered = all(
        st.session_state.get(f"q{i}_answer") is not None
        for i in range(1, len(questions.data) + 1)
    )

    # continue for submission only if all questions have been answered
    if get_submitted and not all_answered:
        st.error("Please answer all of the questions before submitting")
        return 

    response_info = None
    try:
        response_info = responses_repo.get_responses_by_questionnaire_id(user_id, questionnaire_id, False)
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    if response_info is None:
        st.error("Error while checking for user's draft. Please, try again later.")
        return

    if len(response_info.data) == 0:

        # If there is not any draft response for the questionnaire by the user, insert a new response row
        response_insert = None
        try:
            response_insert = responses_repo.create_response(st.session_state["user_id"], questionnaire_id, get_submitted)
        except RuntimeError as e:
            logger.error(f"Database error: {e}")

        if response_insert is None:
            st.error("Error during response's submission. Please, try again later.")
            return

        # create the list with the answer table inserts with response_id the new response insert
        answer_list = []
        for index,question in enumerate(questions.data):
            key = f"q{index+1}_answer"
            answer_list.append({ 
                "response_id": response_insert.data[0]["id"], 
                "question_id": question["id"], 
                "selected_option_value": st.session_state[key]
            })

        # insert the answer list items in the answer's table
        answer_insert = None
        try:
            answer_insert = answers_repo.create_answers(answer_list)
        except RuntimeError as e:
            logger.error(f"Database error: {e}")

        if answer_insert is None:
            st.error("Error during answers' submission. Please, try again later.")
            return
    
        return[response_insert, answer_insert]

    else:

        answers_list = []
            
        for index,question in enumerate(questions.data):
            key = f"q{index+1}_answer"
            answers_list.append({ 
                "response_id": response_info.data[0]["id"], 
                "question_id": question["id"], 
                "selected_option_value": st.session_state[key]
            })

        answers_update = None
        try:
            answers_update = answers_repo.update_answers(answers_list)
        except RuntimeError as e:
            logger.error(f"Database error: {e}")

        if answers_update is None:
            st.error("Error during the update of the answers. Please, try again later.")
            return

        if get_submitted == True:
            update_response = None
            try:
                update_response = responses_repo.update_response_on_submitted(st.session_state["user_id"], get_submitted)
            except RuntimeError as e:
                logger.error(f"Database error: {e}")

            if update_response is None:
                st.error("Error during response's submission. Please, try again later.")
                return

            return [update_response, answers_update]

        return [response_info, answers_update]