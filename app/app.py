import streamlit as st
import re
import html
from datetime import datetime
from dotenv import load_dotenv

from database.questionnaires import Questionnaires
from database.responses import Responses
from database.profiles import Profiles

from utils import supabase_client 
from utils.components import create_questionnaire_card, create_response_card, create_responses_management_ui
from utils.menu import menu
from utils.redirections import redirect_to_respond_page, redirect_to_view_page
from utils.logger_config import logger

# The environment vars are getting loaded for the whole process of the app
load_dotenv()

current_page = "main_page"

client = supabase_client.get_client()
questionnaires_repo = Questionnaires(client)
responses_repo = Responses(client)
profiles_repo = Profiles(client)

def init_ui_state():
    state_values = {
        "create_questionnaire": False,
        "add_questions": False,
        "show_preview": False,
        "create_profile": False,
        "update_profile": False,
        "delete_profile": False,
        "current_questionnaire_id": None,
        "current_response_id": None,
    }

    for key, value in state_values.items():
        st.session_state[key] = value

# -----------------------------------------
# Below starts the UI of the app
# -----------------------------------------

if __name__ == "__main__":
    
    if "last_page" not in st.session_state:
        init_ui_state()
        st.session_state.last_page = current_page

    menu(client)
    st.session_state.last_page = current_page

    user_profile = None
    try:
        user_profile = profiles_repo.get_profile_by_id(st.session_state["user_id"])
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    if user_profile is None:
        st.error("Error during your profile retrieval")
        st.stop
    elif len(user_profile.data) == 0:
        st.session_state["profile_id"] = None
    else:
        st.session_state["profile_id"] = user_profile.data[0]["id"]

    st.title("Welcome to TAMQuest")

    
    if st.session_state["role"] == 'admin':
        st.write("## User's responses")

        responses = None
        try:
            responses = responses_repo.get_all_responses()
        except RuntimeError as e:
            logger.error(f"Database error: {e}")

        if responses is None:
            st.error("Error during the responses retrieval")
        elif len(responses.data) == 0:
            st.write("There are not any responses for the questionnaires")
        else:
            response_list = responses.data

            for response in response_list:
                create_responses_management_ui(response, response["id"], "View",  redirect_to_view_page)

    else:
        
        qs = None
        try:
            qs = questionnaires_repo.questionnaires_without_user_response(st.session_state["user_id"])
        except RuntimeError as e:
            logger.error(f"Database error: {e}")
        
        if qs is None:
            st.error(f"Error during the questionnaires retrieval")
        elif len(qs.data) == 0:
            st.write("There are no questionnaires available for response")
        else:
            questionnaire_list = qs.data

            for item in questionnaire_list:
                
                message_box = st.empty()

                col1, col2 = st.columns([4,1])
        
                with col1:
                    create_questionnaire_card(item)
                
                with col2:
                    respond_key = f"respond_{item['id']}"
                    if st.button("Respond", key=respond_key):
                        if st.session_state["profile_id"] is None:
                            message_box.error("You have to create a profile before submitting a response")
                        else:
                            redirect_to_respond_page(item['id'])

    
    st.write(st.session_state)

                


        


                
