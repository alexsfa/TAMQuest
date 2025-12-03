import streamlit as st
import re
from datetime import datetime
from scripts import supabase_client 
from scripts.menu import menu

client = supabase_client.get_client()

LIKERT_SCALE = [
    "Strongly disagree", 
    "Disagree", 
    "Neutral", 
    "Agree", 
    "Strongly agree"
]

def set_response_ui(questions):
    for question_index, question in enumerate(questions.data, start=1):
        question_key = f"q{question_index}_answer"

        st.markdown(f"</br></br>", unsafe_allow_html=True)
        st.markdown(f"<h5 style='margin-bottom:-50px'>{question_index}. {question['question_text']}</h5>", unsafe_allow_html=True)
        selected_answer = st.radio(
            label="",               
            options=[option for option in LIKERT_SCALE],  
            key=question_key,
            horizontal=True,
            index=None         
        )
    st.markdown(f"</br></br>", unsafe_allow_html=True)
        


def retrieve_questionnaire(questionnaire_id: str):
    questionnaire_info = client.table("questionnaires").select("id, title, details, created_at").eq("id", questionnaire_id).execute()
    questions_info = client.table("questions").select("id, question_text").eq("questionnaire_id", questionnaire_id).execute()
    return [questionnaire_info, questions_info]

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
        r"\.(\d{5})(\+|\-)",   # match .12345+00
        lambda m: f".{m.group(1)}0{m.group(2)}", 
        raw
    )
    dt = datetime.fromisoformat(raw)
    formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    st.write(formatted_time)

    questions = current_questionnaire[1]
    set_response_ui(questions)

    col1, col2 = st.columns([1,1])

    with col1:
        if st.button("Submit"):
            submit_response(st.session_state["user_id"], current_questionnaire[0].data[0]["id"], True, questions)

    with col2:
        if st.button("Save Draft"):
            submit_response(st.session_state["user_id"], current_questionnaire[0].data[0]["id"], False, questions)


