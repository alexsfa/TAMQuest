import streamlit as st
import uuid
import html, re
from pprint import pprint, pformat
from datetime import datetime

from database.questionnaires import Questionnaires
from database.questions import Questions
from database.profiles import Profiles

from services.generate_questionnaires import generate_tam_questions, generate_additional_tam_questions,ESSENTIAL_TAM_QUESTIONS, ADDITIONAL_TAM_QUESTIONS
from services.database_service import submit_questionnaire

from utils import supabase_client 
from utils.menu import menu
from utils.logger_config import logger
from utils.components import create_questionnaire_card, create_profile_card, preview_questionnaire

from app import redirect_to_respond_page

current_page = "admin_page"

client = supabase_client.get_client()
questionnaires_repo = Questionnaires(client)
questions_repo = Questions(client)
profiles_repo = Profiles(client)

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

def restart_questionnaire_ui_state():
    st.session_state.create_questionnaire = False
    st.session_state.add_questions = False
    st.session_state.show_preview = False
    
if __name__ == "__main__":
    st.write(st.session_state)
    menu(client)
    if st.session_state.last_page != current_page:
        restart_questionnaire_ui_state()
        st.session_state.last_page = current_page

    st.title("Welcome to the admin page") 

    if st.button("Create new questionnaire"):
        st.session_state.create_questionnaire = not st.session_state.create_questionnaire

    if st.session_state.create_questionnaire:
        if st.session_state["profile_id"] is None:
            st.error("You have to create a profile before submitting a questionnaire")
        else:
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
                    preview_questionnaire(st.session_state["app_name"])

            if st.button("Submit Questionnaire"):
                submit_result = []
                submit_result = submit_questionnaire(st.session_state["app_name"], st.session_state["q_details"], st.session_state["user_id"])
                if submit_result is None:
                    st.error("Error during questionnaire submission! Try again later!")
                else:
                    restart_questionnaire_ui_state()
                    st.success("Your questionnaire has been submitted")

    st.divider()
    st.write("## Available questionnaires")

    qs = None
    try:
        qs = questionnaires_repo.get_all_questionnaires(st.session_state["user_id"])
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    if qs is None:
        st.error(f"Error during the retrieval of questionnaires")
    elif len(qs.data) == 0:
        st.write("There are no questionnaires available for response")
    else:
        questionnaire_list = qs.data

        for item in questionnaire_list:
            
            col1, col2, col3 = st.columns([5,1,1])

            with col1:
                create_questionnaire_card(item)

            if len(item["responses"]) == 0:
                with col2:
                    respond_key = f"respond_{item['id']}"
                    if st.button("Respond", key=respond_key):
                        redirect_to_respond_page(item['id'])

                message_box = st.empty()

                with col3:
                    delete_key = f"delete_{item['id']}"
                    if st.button("Delete", key=delete_key):
                        response = None
                        try:
                            response = questionnaires_repo.delete_questionnaire_by_id(item['id'])
                            st.rerun()
                        except RuntimeError as e:
                            logger.error(f"Database error: {e}")

                        if response is None:
                            st.error("Error during the delete of the questionnaire")
        
                    st.write("\n")
            else:
                message_box = st.empty()

                with col2:
                    delete_key = f"delete_{item['id']}"
                    if st.button("Delete", key=delete_key):
                        response = None
                        try:
                            response = questionnaires_repo.delete_questionnaire_by_id(item['id'])
                            st.rerun()
                        except RuntimeError as e:
                            logger.error(f"Database error: {e}")

                        if response is None:
                            st.error("Error during the delete of the questionnaire")
        
                st.write("\n")

    st.divider()
    st.write("## Profiles' list")

    profiles = None
    try:
        profiles = profiles_repo.get_all_profiles(st.session_state["user_id"])
    except RuntimeError as e:
        logger.error(f"Database error: {e}")
        
    if profiles is None:
        st.error("Error during the profiles list retrieval")
    elif len(profiles.data) == 0:
        st.write("There are not any users yet.")
    else:
        cols = st.columns(3)
        for i, profile in enumerate(profiles.data):
            col = cols[i % 3]
            with col:
                create_profile_card(profile)

                delete_key = f"delete_{profile['id']}"
                if st.button("Delete", key=delete_key):
                    response = None
                    try:
                        response = profiles_repo.delete_profile_by_id(profile['id'])
                        st.rerun()
                    except RuntimeError as e:
                        logger.error(f"Database error: {e}")

                    if response is None:
                        st.error("Error during the profile's deletion")
                st.markdown("</div>", unsafe_allow_html=True)

        message_box = st.empty()

    st.write(st.session_state)
