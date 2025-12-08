import streamlit as st
import re
from datetime import datetime
from utils import supabase_client 
from utils.menu import menu
from app import delete_response

client = supabase_client.get_client()

def set_response_view(answers):
    st.markdown(f"</br></br>", unsafe_allow_html=True)
    for answer in enumerate(answers.data):
        st.markdown(f"<h5 style='margin-bottom:2px'>{answer[1]['questions']['position']}. {answer[1]['questions']['question_text']}</h5>", unsafe_allow_html=True)
        st.markdown(f"<h5 style='margin-bottom:'>Answer: {answer[1]['selected_option_value']}", unsafe_allow_html=True)
        st.markdown(f"</br></br>", unsafe_allow_html=True)

def retrieve_response_info(response_id: str):
    questionnaire = client.table("responses").select("questionnaires(title, details, created_at), profiles(full_name), submitted_at").eq("id", response_id).execute()
    answers = client.table("answers").select("questions(question_text, position), selected_option_value").eq("response_id", response_id).order("questions(position)").execute()

    return [questionnaire, answers]

if __name__ == "__main__":
    menu(client)

    response_info = retrieve_response_info(st.session_state["current_response_id"])

    st.title(response_info[0].data[0]['questionnaires']['title'])
    st.write(f"Questionnaire description: {response_info[0].data[0]['questionnaires']['details']}")

    raw = response_info[0].data[0]['submitted_at']
    raw = re.sub(
            r"\.(\d+)(?=[+-])",
            lambda m: "." + (m.group(1) + "000000")[:6],
            raw
        )
    dt = datetime.fromisoformat(raw)
    formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S %Z")

    st.write(f"Submitted at {formatted_time}")
    st.write(f"By {response_info[0].data[0]['profiles']['full_name']}")

    set_response_view(response_info[1])
    