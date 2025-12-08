import streamlit as st

def redirect_to_respond_page(questionnaire_id: str):
    st.session_state["current_response_id"] = questionnaire_id
    st.switch_page("pages/questionnaire_response_page.py")

def redirect_to_view_page(response_id: str):
    st.session_state["current_response_id"] = response_id
    st.switch_page("pages/response_view_page.py")