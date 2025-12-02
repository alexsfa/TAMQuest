import streamlit as st
from pprint import pprint, pformat
from scripts.generate_questionnaires import generate_tam_questions, generate_additional_tam_questions,ESSENTIAL_TAM_QUESTIONS, ADDITIONAL_TAM_QUESTIONS
from scripts import supabase_client 
from scripts.menu import menu
import uuid

current_page = "admin_page"

client = supabase_client.get_client()

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

LIKERT_SCALE = ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"]

radio_options = ["Yes", "No"]

def init_questionnaire_ui_state():
    if "create_questionnaire" not in st.session_state:
        st.session_state.create_questionnaire = False

    if "add_questions" not in st.session_state:
        st.session_state.add_questions = False

    if "show_preview" not in st.session_state:
        st.session_state.show_preview = False

def restart_questionnaire_ui_state():
    if st.session_state.create_questionnaire:
        st.session_state.create_questionnaire = False

    if st.session_state.add_questions:
        st.session_state.add_questions = False

    if st.session_state.show_preview:
        st.session_state.show_preview = False

def preview_questionnaire():
    if st.session_state.get("app_name").strip() == "":
        st.warning("Please enter an app name.")
        return

    questions = generate_tam_questions(ESSENTIAL_TAM_QUESTIONS, st.session_state.app_name)

    if "add_questions" in st.session_state and st.session_state["add_questions"]:
        questions.update(generate_additional_tam_questions(ADDITIONAL_TAM_QUESTIONS, st.session_state.app_name))

    for category, questions in questions.items():
        st.markdown(f"### **{category}**" + "\n".join(f"\n{i+1} - {q}" for i, q in enumerate(questions)))

    

def submit_questionnaire():

    if st.session_state.get("app_name").strip() == "":
        st.warning("Please enter an app name.")
        return

    q_details = st.session_state.get("q_details", "")

    if q_details and q_details.strip():
        questionnaire_details = q_details.strip()
    else:
        questionnaire_details = None

    questionnaire_insert = client.table("questionnaires").insert({
        "title": f"TAM Questionnaire for {st.session_state.app_name}",
        "details": questionnaire_details,
        "created_by": st.session_state["user_id"]
    }).execute()

    if not questionnaire_insert.data:
        raise Exception("Failed to create questionnaire")

    questionnaire_id = questionnaire_insert.data[0]["id"]

    questions = generate_tam_questions(ESSENTIAL_TAM_QUESTIONS, st.session_state.app_name)

    if "add_questions" in st.session_state and st.session_state["add_questions"]:
        questions.update(generate_additional_tam_questions(ADDITIONAL_TAM_QUESTIONS, st.session_state.app_name))

    for category, qs in questions.items():
        for position, question_text in enumerate(qs):
            question_insert = client.table("questions").insert({
                "questionnaire_id": questionnaire_id,
                "question_text": question_text,
                "position": position
            }).execute()

            question_id = question_insert.data[0]["id"]

        if not question_insert.data:
            raise Exception("Failed to insert question.")

    st.write(st.session_state.create_questionnaire)
    st.write(st.session_state.add_questions)
    st.write(st.session_state.show_preview)
    st.success("Your questionnaire has been submitted!")
    restart_questionnaire_ui_state()
    st.write(st.session_state.create_questionnaire)
    st.write(st.session_state.add_questions)
    st.write(st.session_state.show_preview)
    
    


if __name__ == "__main__":

    client = supabase_client.get_client()
    menu(client)

    init_questionnaire_ui_state()

    if st.session_state.last_page != current_page:
        restart_questionnaire_ui_state()
        st.session_state.last_page = current_page
    
    st.title("Welcome to the admin page") 

    if st.button("Create new questionnaire"):
        st.session_state.create_questionnaire = not st.session_state.create_questionnaire

    if st.session_state.create_questionnaire:
        st.text_input("The name of the app", key="app_name")

        st.text_area("Enter details about the questionnaire", height=150, key="q_details")

        if "add_questions" not in st.session_state:
            st.session_state.add_questions = False

        if "show_preview" not in st.session_state:
            st.session_state.show_preview = False

        button_1, button_2 = st.columns(2)
        with button_1:
            if st.button("Add additional questions"):
                st.session_state.add_questions = not st.session_state.add_questions

        with button_2:
            if st.button("Preview Questionnaire"):
                st.session_state.show_preview = not st.session_state.show_preview

        additional_questions_container = st.container()
 
        with additional_questions_container:
            if st.session_state.add_questions:
                cols = st.columns(2)

                for i, (label, key) in enumerate(additional_question_configs):
                    col = cols[i % 2]
                    col.checkbox(label, key=key)
            else:
                additional_questions_container.empty()

        questionnaire_preview_container = st.container()

        with questionnaire_preview_container:
            if st.session_state.show_preview:
                preview_questionnaire()

        if st.button("Submit Questionnaire"):
            try:
                submit_questionnaire()
            except Exception as e:
                st.error(f"Failed to create questionnaire: {e}")
