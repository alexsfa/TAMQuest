import streamlit as st
from datetime import date
import html, re
from datetime import datetime

from database.profiles import Profiles

from utils import supabase_client 
from utils.menu import menu
from utils.redirections import redirect_to_respond_page, redirect_to_view_page
from utils.logger_config import logger

current_page = "profile_page"

client = supabase_client.get_client()
profiles_repo = Profiles(client)


# The function init_profile_ui() initializes the fields of the session state 
# that control the profile UI if the user visits the profile_page for the first time.
def init_profile_ui():
    if "create_profile" not in st.session_state:
        st.session_state.create_profile = False

    if "update_profile" not in st.session_state:
        st.session_state.update_profile = False

    if "delete_profile" not in st.session_state:
        st.session_state.delete_profile = False


# The function render_profile_form renders the form with the profile fields
# so the user can create his own profile or update it.
def render_profile_form(mode: str):
    username = st.text_input("Your name", key=f"{mode}_username")
    birthdate = st.date_input(
        f"{mode}_birthdate", 
        max_value=date.today(),
        min_value=date(1900, 1, 1))
    city = st.text_input("Your city", key=f"{mode}_user_city")
    country = st.text_input("Your country", key=f"{mode}_user_country")
    return [username, birthdate.isoformat(), city, country]

if __name__ == "__main__":

    client = supabase_client.get_client()
    menu(client)

    init_profile_ui()

    if st.session_state.last_page != current_page:
        st.session_state.create_profile = False
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
        
        # TO-DO: Add a function that standarize spacing across the whole app
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
            profile_inputs = render_profile_form("insert")

            profile_insert = None
            if st.button("Create"):
                try:
                    profile_insert = profiles_repo.create_profile(st.session_state["user_id"], profile_inputs[0], profile_inputs[1], profile_inputs[2], profile_inputs[3])
                    st.write(profile_insert)
                except RuntimeError as e:
                    logger.error(f"Database error: {e}")

                if profile_insert is None:
                    raise Exception("Failed to create profile.")
                else:
                    st.session_state.create_profile = False
                    st.rerun()

        if st.session_state.update_profile:
            profile_inputs = render_profile_form("update")

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
                        st.session_state.delete_profile = False
                        st.rerun()

            with col2:
                if st.button("No", key="cancel_delete"):
                    st.session_state.delete_profile = False
                    st.rerun()

    st.divider()
    st.title("Your responses")

    responses = client.table("responses").select("questionnaires(*), id, submitted_at, is_submitted").eq("user_id", st.session_state["user_id"]).order("is_submitted", desc=True).execute()

    drafts = [r for r in responses.data if not r["is_submitted"]]
    submitted = [r for r in responses.data if r["is_submitted"]]

    if len(submitted) == 0:
        st.write("There are no responses")
    else:

        for item in submitted:

            title_safe = html.escape(item['questionnaires']['title'])

            raw = item["submitted_at"]
            raw = re.sub(
                r"\.(\d+)(?=[+-])",
                lambda m: "." + (m.group(1) + "000000")[:6],
                raw
            )
            dt = datetime.fromisoformat(raw)
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S %Z")

            col1, col2 = st.columns([3,1])
        
            with col1:
                st.markdown(f"""
                    <article style='
                        border: 4px solid #000000; 
                        background-color: #E4EDA6;
                        padding:8px;
                        border-radius:8px;
                        margin-bottom:12px;
                        text-align: center;'>
                        <small>Response for:</small><br>
                        <h3>{title_safe}</h3>
                        <small>Submitted at: {formatted_time}</small><br>
                    </article>
                    """, unsafe_allow_html=True)
                
            with col2:
                respond_key = f"view_{item['id']}"
                if st.button("View", key=respond_key):
                    redirect_to_view_page(item['id'])

    st.divider()

    st.title("Your drafts")

    if len(drafts) == 0:
        st.write("There are no drafts")
    else:

        for item in drafts:

            title_safe = html.escape(item['questionnaires']['title'])

            raw = item["submitted_at"]
            raw = re.sub(
                r"\.(\d+)(?=[+-])",
                lambda m: "." + (m.group(1) + "000000")[:6],
                raw
            )
            dt = datetime.fromisoformat(raw)
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S %Z")

            col1, col2 = st.columns([3,1])
        
            with col1:
                st.markdown(f"""
                    <article style='
                        border: 4px solid #000000; 
                        background-color: #E4EDA6;
                        padding:8px;
                        border-radius:8px;
                        margin-bottom:12px;
                        text-align: center;'>
                        <small>Response draft for:</small><br>
                        <h3>{title_safe}</h3>
                        <small>Saved at: {formatted_time}</small><br>
                    </article>
                    """, unsafe_allow_html=True)
                
            with col2:
                respond_key = f"edit_{item['questionnaires']['id']}"
                if st.button("Edit", key=respond_key):
                    redirect_to_respond_page(item["questionnaires"]['id'])
    