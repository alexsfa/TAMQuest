import os
from menu import menu
from dotenv import load_dotenv
import streamlit as st
from supabase import create_client, Client
import streamlit.components.v1 as components
from datetime import date

# Loads the environment variables
load_dotenv()

SUPABASE_KEY = os.getenv("ANON_KEY")

BASE_URL = os.getenv("SUPABASE_URL")
supabase: Client = create_client(BASE_URL, SUPABASE_KEY)

if "role" not in st.session_state:
    st.session_state.role = None

st.session_state._role = st.session_state.role

def set_role():
    st.session_state.role = st.session_state._role

st.selectbox(
    "Select your role:",
    [None, "user", "admin"],
    key="_role",
    on_change=set_role,
)

menu()


def login_user(email: str, password: str):
    try:
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state["user"] = user
        st.success(f"Logged in as {user.user.email}")
    except Exception as e:
        st.error(f"Log in has failed:{e}")

def signup_user(email:str, password: str, name:str, birthdate):
    try:
        birthdate_str = birthdate.isoformat()
        st.write(birthdate_str)
        supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": { 
                    "role": "user",
                    "name": name,
                    "birthdate": birthdate_str
                    }
                }
            })
        st.success("Signed up successfully. Please check your email for confirmation.")
    except Exception as e:
        st.error(f"Sign up has failed: {e}")

def logout_user():
    st.session_state["user"] = None
    st.success("Logged out")

# -----------------------------------------
# Below starts the UI of the app
# -----------------------------------------

st.title("Private App Login")

if st.session_state["user"] is None:
    st.header("Please log in")

    auth_action = st.selectbox("Choose action", ["Login", "Sign up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if auth_action == "Sign up":
        name = st.text_input("Name")
        birthdate = st.date_input(
                        "Birthdate", 
                        max_value=date.today(),
                        min_value=date(1900, 1, 1))

        if st.button("Sign up"):
            signup_user(email, password, name, birthdate)

    elif auth_action == "Login" and st.button("Login"):
        login_user(email, password)

else:
    st.success(f"Logged in as {st.session_state['user'].user.email}")
    if st.button("Log out"):
        logout_user()