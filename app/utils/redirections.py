import streamlit as st

def redirect_to_respond_page(questionnaire_id: str):
    st.session_state["current_questionnaire_id"] = questionnaire_id
    st.session_state["edit_response_mode"] = False
    st.switch_page("pages/questionnaire_response_page.py")

def redirect_to_edit_page(response_id: str):
    st.session_state["current_response_id"] = response_id
    st.session_state["edit_response_mode"] = True
    st.switch_page("pages/questionnaire_response_page.py")

'''
The redirect_to_view_page function sets the current_respond_id and redirects to response view page
'''
def redirect_to_view_page(response_id: str):
    st.session_state["current_response_id"] = response_id
    st.switch_page("pages/response_view_page.py")