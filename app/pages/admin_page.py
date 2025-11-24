import streamlit as st
from scripts.generate_questionnaires import generate_tam_questions, generate_additional_tam_questions,ESSENTIAL_TAM_QUESTIONS, ADDITIONAL_TAM_QUESTIONS
from scripts import supabase_client 
from scripts.menu import menu

current_page = "admin_page"

additional_question_configs = [
    ("Technology support questions", "Technology Support"),
    ("User satisfaction questions", "User Satisfaction"),
    ("Computer anxiety questions", "Computer Anxiety"),
    ("Computer self-efficacy questions", "Computer Self-Efficacy"),
    ("Compatibility questions", "Compatibility"),
    ("Information quality questions", "Information Quality"),
    ("System quality questions", "System Quality"),
    ("Risk questions", "Risk"),
    ("Subjective norm questions", "Subjective Norm"),
    ("Behavioral control questions", "Behavioral Control"),
    ("Trust questions", "Trust"),
]

radio_options = ["Yes", "No"]

def preview_questionnaire():
    if st.session_state.get("app_name").strip() == "":
        st.warning("Please enter an app name before submitting.")
        return
    st.write(generate_tam_questions(ESSENTIAL_TAM_QUESTIONS, st.session_state.app_name))
    if st.session_state["add_questions"]:
        st.write(generate_additional_tam_questions(ADDITIONAL_TAM_QUESTIONS, st.session_state.app_name))

def submit_questionnaire():
    st.success("Questionnaire created!")

if __name__ == "__main__":

    client = supabase_client.get_client()
    menu(client)

    if st.session_state.last_page != current_page:

        if "create_questionnaire" in st.session_state:
            st.session_state.create_questionnaire = False

        if "add_questions" in st.session_state:
            st.session_state.add_questions = False

        st.session_state.last_page = current_page
    
    st.title("Welcome to the admin page")

    if "create_questionnaire" not in st.session_state:
        st.session_state.create_questionnaire = False

    if st.button("Create new questionnaire"):
        st.session_state.create_questionnaire = not st.session_state.create_questionnaire

    if st.session_state.create_questionnaire:
        app_name = st.text_input("The name of the app", key="app_name")

        if "add_questions" not in st.session_state:
            st.session_state.add_questions = False

        if st.button("Add additional questions"):
            st.session_state.add_questions = not st.session_state.add_questions

        if st.session_state.add_questions:
            cols = st.columns(2)

            for i, (label, key) in enumerate(additional_question_configs):
                col = cols[i % 2]
                col.checkbox(label, key=key)

        if st.button("Preview Questionnaire"):
            preview_questionnaire()

        if st.button("Submit Questionnaire"):
            submit_questionnaire()





