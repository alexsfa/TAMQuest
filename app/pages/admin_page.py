import streamlit as st
import uuid
import html, re
from pprint import pprint, pformat
from datetime import datetime

from database.questionnaires import Questionnaires
from database.questions import Questions
from database.profiles import Profiles

from utils.generate_questionnaires import generate_tam_questions, generate_additional_tam_questions,ESSENTIAL_TAM_QUESTIONS, ADDITIONAL_TAM_QUESTIONS
from utils import supabase_client 
from utils.menu import menu
from utils.logger_config import logger

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


# The function init_profile_ui() initializes the fields of the session state that control the UI
# about the creation of a questionnaire if the admin visits the profile_page for the first time.
def init_questionnaire_ui_state():
    if "create_questionnaire" not in st.session_state:
        st.session_state.create_questionnaire = False

    if "add_questions" not in st.session_state:
        st.session_state.add_questions = False

    if "show_preview" not in st.session_state:
        st.session_state.show_preview = False

    if "submit_success" not in st.session_state:
        st.session_state.submit_success = False

def restart_questionnaire_ui_state():
    st.session_state.create_questionnaire = False
    st.session_state.add_questions = False
    st.session_state.show_preview = False
        

# The function preview_questionnaire() renders on the page the selected by the user questions
# that the questionnaire will include.
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

    questionnaire = None
    try:
        questionnaire = questionnaires_repo.create_questionnaire(st.session_state.get("app_name"), q_details, st.session_state.get("user_id"))
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    if questionnaire is None:
        st.write(questionnaire)
        st.error("Error during the questionnaire 's creation")
        return

    questions = generate_tam_questions(ESSENTIAL_TAM_QUESTIONS, st.session_state.app_name)

    if "add_questions" in st.session_state and st.session_state["add_questions"]:
        questions.update(generate_additional_tam_questions(ADDITIONAL_TAM_QUESTIONS, st.session_state.app_name))

    questions_to_insert = []
    position = 1

    for category, qs in questions.items():
        for question_text in qs:
            questions_to_insert.append({
                "questionnaire_id": questionnaire.data[0]["id"],
                "question_text": question_text,
                "position": position
            })
            position += 1

    try:   
        response = questions_repo.create_questions(questions_to_insert)
        if "error" in response:
            raise Exception(response.error['message'])
    except Exception as e:
        st.error(f"Error during the questions' submission: {e}")

    restart_questionnaire_ui_state()
    st.success("Your questionnaire has been submitted")
    
    
if __name__ == "__main__":

    menu(client)

    if st.session_state.last_page != current_page:
        init_questionnaire_ui_state()
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
                restart_questionnaire_ui_state()
            except Exception as e:
                st.error(f"Failed to create questionnaire: {e}")

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
            title_safe = html.escape(item['title'])

            if item['details'] is None:
                details_safe = "No details were provided."
            else: 
                details_safe = html.escape(item['details'])

            raw = item["created_at"]
            raw = re.sub(
                r"\.(\d+)(?=[+-])",
                lambda m: "." + (m.group(1) + "000000")[:6],
                raw
            )
            dt = datetime.fromisoformat(raw)
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S %Z")

            questionnaire_card = st.container()

            col1, col2, col3 = st.columns([5,1,1])
        
            with col1:
                st.markdown(f"""
                    <article style='
                        border: 4px solid #000000; 
                        background-color: #E4EDA6;
                        padding:8px;
                        border-radius:8px;
                        margin-bottom:12px;
                        text-align: center;'>
                        <h3>{title_safe}</h3>
                        <p style='font-size:18px;'>{details_safe}</p>
                        <small>Created at: {formatted_time}</small><br>
                    </article>
                    """, unsafe_allow_html=True)

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
        profiles = profiles_repo.get_all_profiles()
    except RuntimeError as e:
        logger.error(f"Database error: {e}")
        
    if profiles is None:
        st.error("Error during the profiles list retrieval")
    elif len(profiles.data) == 0:
        st.write("There are not any users yet.")
    else:
        cols = st.columns(3)
        for i, profile in enumerate(profiles.data):
            user_name = html.escape(profile["full_name"])
            user_birthdate = html.escape(profile["birthdate"])
            user_city = html.escape(profile["city"])
            user_country = html.escape(profile["country"])

            col = cols[i % 3]
            with col:
                st.markdown(f"""
                    <article style='
                        border: 4px solid #000000; 
                        background-color: #B2FBE6;
                        border-radius:8px;
                        padding-top: 12px;
                        margin-bottom:12px;
                        text-align: center;'>
                        <p style='font-size:18px;'>{user_name}</p>
                        <p style='font-size:18px;'>{user_birthdate}</p>
                        <p style='font-size:18px;'>{user_country}, {user_city}</p>
                    </article>
                    """, unsafe_allow_html=True)

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
