import streamlit as st
import re
from datetime import datetime

from database.questionnaires import Questionnaires
from database.questions import Questions

from utils import supabase_client 
from utils.menu import menu
from utils.logger_config import logger

client = supabase_client.get_client()
questionnaires_repo = Questionnaires(client)
questions_repo = Questions(client)

LIKERT_SCALE = [
    (0,"Strongly disagree"), 
    (1,"Disagree"), 
    (2,"Neutral"), 
    (3,"Agree"), 
    (4,"Strongly agree")
]

def set_response_ui(questions, draft_answers):

    if len(draft_answers) == 0:
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
        indexes = [
            next((i for i, (num, text) in enumerate(LIKERT_SCALE) if text == ans), None)
            for ans in draft_answers
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
    response_info = client.table("responses").select("id").eq("user_id", st.session_state["user_id"]).eq("questionnaire_id", questionnaire_id).eq("is_submitted", False).execute()
    draft_answers = []

    if len(response_info.data) == 0:
        pass
    else:
        answers = client.table("answers").select("*, questions(position)").eq("response_id", response_info.data[0]["id"]).order("questions(position)").execute()
        for answer in answers.data:
            draft_answers.append(answer["selected_option_value"])

    return draft_answers


def submit_response(user_id:str, questionnaire_id: str, get_submitted: bool, questions):

    all_answered = all(
        st.session_state.get(f"q{i}_answer") is not None
        for i in range(1, len(questions.data) + 1)
    )

    if get_submitted and not all_answered:
        st.error("Please answer all of the questions before submitting")
        return None

    response_info = client.table("responses").select("id").eq("user_id", user_id).eq("questionnaire_id", questionnaire_id).eq("is_submitted", False).execute()

    if len(response_info.data) == 0:
        response_insert = client.table("responses").insert({
            "user_id": user_id,
            "questionnaire_id": questionnaire_id,
            "is_submitted": get_submitted
        }).execute()

        for index,question in enumerate(questions.data):
            key = f"q{index+1}_answer"
            answer_insert = client.table("answers").insert({
                "response_id": response_insert.data[0]["id"],
                "question_id": question["id"],
                "selected_option_value": st.session_state[key]
            }).execute()

    else:
    

        for index,question in enumerate(questions.data):
            key = f"q{index+1}_answer"

            answer_insert = (
                client.table("answers")
                .update({"selected_option_value": st.session_state[key]})
                .eq("response_id", response_info.data[0]["id"])
                .eq("question_id", question["id"])
                .execute()
            )

        if get_submitted == True:
            response = client.table("responses").update({"is_submitted": get_submitted}).eq("id", response_info.data[0]["id"]).execute()

            if not response:
                st.error(f"Submit failed! Try later!")


if __name__ == "__main__":
    menu(client)

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
    draft_answers = retrieve_draft(current_questionnaire[0].data[0]["id"])
    set_response_ui(questions, draft_answers)
    

    col1, col2 = st.columns([1,1])

    with col1:
        if st.button("Submit"):
            submit_response(st.session_state["user_id"], current_questionnaire[0].data[0]["id"], True, questions)

    with col2:
        if st.button("Save Draft"):
            submit_response(st.session_state["user_id"], current_questionnaire[0].data[0]["id"], False, questions)


