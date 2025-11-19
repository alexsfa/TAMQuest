import streamlit as st
from datetime import date

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