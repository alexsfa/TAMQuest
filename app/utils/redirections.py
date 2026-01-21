import streamlit as st

'''
The redirect_to_respond_page function redirects to a questionnaire's response page
The response gets specified by its questionnaire id.
'''
def redirect_to_respond_page(questionnaire_id: str):
    st.session_state["current_questionnaire_id"] = questionnaire_id
    st.session_state["edit_response_mode"] = False
    st.switch_page("pages/questionnaire_response_page.py")

'''
The redirect_to_respond_page function redirects to a questionnaire's results page.
The questionnaire gets specified by its id.
'''
def redirect_to_results_page(questionnaire_id: str):
    st.session_state["current_questionnaire_id"] = questionnaire_id
    st.switch_page("pages/questionnaire_results_page.py")

'''
The redirect_to_edit_page function redirects to a response's edit page
The response gets specified by its id.
'''
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