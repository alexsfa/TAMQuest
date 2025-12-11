import streamlit as st
from datetime import date
import html, re

from database.profiles import Profiles
from database.responses import Responses

from utils import supabase_client 
from utils.menu import menu
from utils.logger_config import logger
from utils.components import create_response_card, create_profile_form, create_responses_management_ui
from utils.redirections import redirect_to_respond_page, redirect_to_view_page, redirect_to_edit_page

client = supabase_client.get_client()
profiles_repo = Profiles(client)
responses_repo = Responses(client)

current_page = "profile_page"

def restart_profile_ui_state():
    st.session_state["create_profile"] = False
    st.session_state["update_profile"] = False
    st.session_state["delete_profile"] = False

if __name__ == "__main__":
    
    menu(client)
    if st.session_state.last_page != current_page:
        restart_profile_ui_state()
        st.session_state.last_page = current_page

    st.title("Welcome to your profile")

    user_profile = None
    try:
        user_profile = profiles_repo.get_profile_by_id(st.session_state["user_id"])
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    if user_profile is None:
        st.error("Error during profile's retrieval")
    elif len(user_profile.data) == 0:
        if st.button("Create your profile"):
            st.session_state.create_profile = not st.session_state.create_profile
    else:
        st.write(f"##### Full name: {user_profile.data[0]['full_name']}")
        st.write(f"##### Birthdate: {user_profile.data[0]['birthdate']}")
        st.write(f"##### Location: {user_profile.data[0]['country']}, {user_profile.data[0]['city']}")
        
        st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
        

        col1, col2 = st.columns([1,1])

        with col1:
            if st.button("Update your profile"):
                st.session_state.update_profile = not st.session_state.update_profile

        with col2:
            if st.button("Delete your profile"):
                st.session_state.delete_profile = not st.session_state.delete_profile

    with st.container():

        if st.session_state.create_profile:
            profile_inputs = create_profile_form("insert")

            if st.button("Create"):
                profile_insert = None
                try:
                    profile_insert = profiles_repo.create_profile(st.session_state["user_id"], profile_inputs[0], profile_inputs[1], profile_inputs[2], profile_inputs[3])
                except RuntimeError as e:
                    logger.error(f"Database error: {e}")

                if profile_insert is None:
                    raise Exception("Failed to create profile.")
                else:
                    st.session_state["profile_id"] = profile_insert.data[0]["id"]
                    st.session_state.create_profile = False
                    st.rerun()

        if st.session_state.update_profile:
            profile_inputs = create_profile_form("update")

            if st.button("Update"):
                profile_update = None
                try:
                    profile_update = profiles_repo.update_profile_by_id(
                        st.session_state["user_id"], profile_inputs[0], profile_inputs[1],
                        profile_inputs[2], profile_inputs[3],user_profile.data[0]['full_name'],
                        user_profile.data[0]['birthdate'],user_profile.data[0]['city'],user_profile.data[0]['country']
                    )
                except RuntimeError as e:
                    logger.error(f"Database error: {e}")

                if profile_update is None:
                    st.error("Error during profile update attempt.")
                else:
                    st.session_state.update_profile = False
                    st.rerun()
    
        if st.session_state.delete_profile:
            st.warning("Are you sure about deleting your profile?")

            col1, col2 = st.columns([1,1])

            with col1:
                if st.button("Yes", key="confirm_delete"):
                    profile_delete = None
                    try:
                        profile_delete = profiles_repo.delete_profile_by_id(st.session_state["user_id"])
                    except RuntimeError as e:
                        logger.error(f"Database error: {e}")

                    if profile_delete is None:
                        st.error("Error during the profile's deletion.")
                    else:
                        st.session_state["profile_id"] = None
                        st.session_state.delete_profile = False
                        st.rerun()

            with col2:
                if st.button("No", key="cancel_delete"):
                    st.session_state.delete_profile = False
                    st.rerun()

    st.divider()
    st.title("Your responses")
    
    responses = None
    try:
        responses = responses_repo.get_response_by_user_id(st.session_state["user_id"])
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    drafts, submitted = None, None
    if responses is None:
        drafts = None
        submitted = None
    else:
        drafts = [r for r in responses.data if not r["is_submitted"]]
        submitted = [r for r in responses.data if r["is_submitted"]]

    if submitted is None:
        st.error("There was a problem with the database. Please, try again later.")
    elif len(submitted) == 0:
        st.write("There are no responses")
    else:
        for response in submitted:
            create_responses_management_ui(response, "View",  redirect_to_view_page, user_profile.data[0]['full_name'])

    st.divider()

    st.title("Your drafts")

    if drafts is None:
        st.error("There was a problem with the database. Please, try again later.")
    elif len(drafts) == 0:
        st.write("There are no drafts")
    else:

        for draft in drafts:
            create_responses_management_ui(draft,  "Edit",  redirect_to_edit_page, user_profile.data[0]['full_name'])

    