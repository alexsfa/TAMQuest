import streamlit as st
from datetime import date
from supabase import create_client, Client

def login_user(supabase_client, email: str, password: str):
    try:
        user = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
        role = user.user.app_metadata.get("role", "user")
        st.session_state["role"] = role
        st.session_state["user_id"] = user.user.id
        st.switch_page("app.py")
    except Exception as e:
        st.error(f"Log in has failed:{e}")

def signup_user(supabase_client, email:str, password: str, name:str, birthdate):
    try:
        birthdate_str = birthdate.isoformat()
        st.write(birthdate_str)
        supabase_client.auth.sign_up({
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

def logout_user(supabase_client):
    try:
        supabase_client.auth.sign_out()
    except Exception as e:
        st.error(f"Logout failed: {e}")
    
    keys_to_clear = ["user", "role"]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    st.switch_page("pages/login_page.py")