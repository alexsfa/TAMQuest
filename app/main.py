from dotenv import load_dotenv
import os

from supabase import create_client, Client
import streamlit as st

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SERVICE_ROLE_KEY")

def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()



def login_screen():
    st.header("This app is private.")
    st.subheader("Please log in.")

    auth_action = st.selectbox("Choose action", ["Login", "Sign up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if auth_action == "Sign up":
        if st.button("Sign Up"):
            try:
                new_user = supabase.auth.sign_up({
                    "email": email, 
                    "password": password,
                    "options": {
                        "data": {"role": "user"} 
                    }
                    })
                st.success("Signed up successfully. Please check your email.")
            except Exception as e:
                st.error(f"Error signing up: {e}")

    elif auth_action == "Login":
        if st.button("Login"):
            try:
                user = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state['user'] = user
                st.success(f"Logged in as {user.user.email}")
            except Exception as e:
                    st.error(f"Login failed: {e}")


    st.button("Log in with Google", on_click=st.login)


if not st.user.is_logged_in:
    login_screen()
else:
    st.button("Log out", on_click=st.logout)

