import streamlit as st

from app import profiles_repo, logger
from utils.components import create_profile_form

from utils.redirections import redirect_to_login_page

redirect_to_login_page()

st.title("Create your profile")
profile_inputs = create_profile_form("insert")

if st.button("Create"):
    profile_insert = None
    try:
        profile_insert = (
            profiles_repo.create_profile(
                st.session_state["user_id"],
                profile_inputs[0],
                profile_inputs[1],
                profile_inputs[2],
                profile_inputs[3]
            )
        )
    except RuntimeError as e:
        logger.error(f"Database error: {e}")

    if profile_insert is None:
        raise Exception("Failed to create profile.")
    else:
        st.switch_page("app.py")
