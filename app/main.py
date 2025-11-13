import os
from dotenv import load_dotenv
import streamlit as st
from supabase import create_client, Client
import streamlit.components.v1 as components

# Loads the environment variables
load_dotenv()

BASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SERVICE_ROLE_KEY")

REDIRECT_URI = f"{BASE_URL}/auth/v1/callback"

supabase: Client = create_client(BASE_URL, SUPABASE_KEY)

if "user" not in st.session_state:
    st.session_state["user"] = None

def login_user(email: str, password: str):
    try:
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state["user"] = user
        st.success(f"Logged in as {user.user.email}")
    except Exception as e:
        st.error(f"Log in has failed:{e}")

def signup_user(email:str, password: str):
    try:
        supabase.auth.sign.up({
            "email": email,
            "password": password,
            "options": {"data": {"role": "user"}}
        })
        st.success("Signed up successfully. Please check your email for confirmation.")
    except Exception as e:
        st.error(f"Sign up has failed: {e}")

def logout_user():
    st.session_state["user"] = None
    st.success("Logged out")

def google_oauth_login():
    oauth_url = "f{BASE_URL}/auth/v1/authorize?provider=google&redirect_to={REDIRECT_URI}"
    js = f"""
    <script type="text/javascript">
        window.location.href = "{oauth_url}";
    </script>
    """
    components.html(js)

# -----------------------------------------
# Below starts the UI of the app
# -----------------------------------------

st.title("Private App Login")

if st.session_state["user"] is None:
    st.header("Please log in")

    auth_action = st.selectbox("Choose action", ["Login", "Sign up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if auth_action == "Sign up" and st.button("Sign Up"):
        signup_user(email, password)
    elif auth_action == "Login" and st.button("Login"):
        login_user(email, password)

    st.markdown("---")
    st.subheader("Or log in with Google")
    if st.button("Log in with Google"):
        google_oauth_login()
else:
    st.success(f"Logged in as {st.session_state['user'].user.email}")
    if st.button("Log out"):
        logout_user()