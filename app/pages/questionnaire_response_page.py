import streamlit as st
import re
from datetime import datetime

from database.questionnaires import Questionnaires
from database.questions import Questions
from database.responses import Responses
from database.answers import Answers

from utils import supabase_client 
from utils.menu import menu
from utils.logger_config import logger

client = supabase_client.get_client()
questionnaires_repo = Questionnaires(client)
questions_repo = Questions(client)
responses_repo = Responses(client)
answers_repo = Answers(client)

LIKERT_SCALE = [
    (0,"Strongly disagree"), 
    (1,"Disagree"), 
    (2,"Neutral"), 
    (3,"Agree"), 
    (4,"Strongly agree")
]

def set_response_ui(questions, draft_answers: list | None = None):

    if draft_answers is None:
        for question_index, question in enumerate(questions.data, start=1):
            question_key = f"q{question_index}_answer"

            st.markdown(f"</br></br>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='margin-bottom:-10px'>{question_index}. {question['question_text']}</h5>", unsafe_allow_html=True)
            selected_answer = st.radio(
                label=question['question_text'],     
                options=[option for (num, option) in LIKERT_SCALE],  
                key=question_key,
                horizontal=True,
                index=None,
                label_visibility="collapsed",       
            )
        st.markdown(f"</br></br>", unsafe_allow_html=True)

    else:
        # check which selected_option_value field of draft_answers matches a scale of LIKERT SCALE list
        indexes = [
            next((i for i, (num, text) in enumerate(LIKERT_SCALE) if text == ans["selected_option_value"]), None)
            for ans in draft_answers.data
        ]
        for question_index, question in enumerate(questions.data, start=1):
            question_key = f"q{question_index}_answer"

            st.markdown(f"</br></br>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='margin-bottom:-10px'>{question_index}. {question['question_text']}</h5>", unsafe_allow_html=True)
            selected_answer = st.radio(
                label=question['question_text'],               
                options=[option for (num, option) in LIKERT_SCALE],  
                key=question_key,
                horizontal=True,
                index=indexes[question_index - 1],
                label_visibility="collapsed"
            )
        st.markdown(f"</br></br>", unsafe_allow_html=True)
        


def retrieve_questionnaire(questionnaire_id: str):
    questionnaire_info = None
    try:
        questionnaire_info = questionnaires_repo.get_questionnaire_by_id(questionnaire_id)
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    if questionnaire_info is None:
        st.error("Error during questionnaire's retrieval")
        return
    
    questions_info = None
    try:
        questions_info = questions_repo.get_questions_by_questionnaire_id(questionnaire_id)
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    if questions_info is None:
        st.error("Error during questions' retrieval")
        return

    return [questionnaire_info, questions_info]

def retrieve_draft(questionnaire_id: str):

    response_info = None
    try:
        response_info = responses_repo.get_responses_by_questionnaire_id(st.session_state["user_id"], questionnaire_id, False)
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    return response_info
        

def submit_response(user_id: str,questionnaire_id: str, get_submitted: bool, questions):

    # checking if all the questions have been answered
    all_answered = all(
        st.session_state.get(f"q{i}_answer") is not None
        for i in range(1, len(questions.data) + 1)
    )

    # continue for submission only if all questions have been answered
    if get_submitted and not all_answered:
        st.error("Please answer all of the questions before submitting")
        return None

    response_info = None
    try:

        response_info = responses_repo.get_responses_by_questionnaire_id(st.session_state["user_id"], questionnaire_id, False)

    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    if response_info is None:
        st.error("There was a database error! Try again later!")
    else:
        if len(response_info.data) == 0:

            # If there is not any draft response for the questionnaire by the user, insert a new response row
            response_insert = None
            try:
                response_insert = responses_repo.create_response(st.session_state["user_id"], questionnaire_id, get_submitted)

            except RuntimeError as e:
                logger.error(f"Database error: {e}")

            if response_insert is None:
                st.error("Error during the response submission")
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
                st.error("There was a database error! Try again later!")
        else:
            # if
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
                st.error("There was a database error! Try again later!")

            if get_submitted == True:
                update_response = None
                try:
                    update_response = responses_repo.update_response_on_submitted(st.session_state["user_id"], get_submitted)
                except RuntimeError as e:
                    logger.error(f"Database error: {e}")

                if update_response is None:
                    st.error("There was a databases error! Try again later!")


if __name__ == "__main__":
    menu(client)
    st.write(st.session_state)
    current_questionnaire = retrieve_questionnaire(st.session_state["current_response_id"])
    st.title(current_questionnaire[0].data[0]["title"])

    details_text = current_questionnaire[0].data[0]["details"]
    if details_text is None: 
        st.write("No further details were provided")
    else: 
        st.write(current_questionnaire[0].data[0]["details"])

    raw = current_questionnaire[0].data[0]["created_at"]
    raw = re.sub(
            r"\.(\d+)(?=[+-])",
            lambda m: "." + (m.group(1) + "000000")[:6],
            raw
        )
    dt = datetime.fromisoformat(raw)
    formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    st.write(formatted_time)

    questions = current_questionnaire[1]
    response_draft_info = retrieve_draft(current_questionnaire[0].data[0]["id"])
    if response_draft_info is None:
        st.error("Error during draft search. Try again later!")
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

        set_response_ui(questions, draft_answers)
    

    col1, col2 = st.columns([1,1])

    with col1:
        if st.button("Submit"):
            submit_response(st.session_state["user_id"], current_questionnaire[0].data[0]["id"], True, questions)

    with col2:
        if st.button("Save Draft"):
            submit_response(st.session_state["user_id"], current_questionnaire[0].data[0]["id"], False, questions)


