import streamlit as st
from datetime import date
from supabase import create_client, Client

def login_user(supabase_client, email: str, password: str):
    try:
        user = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
        return user
    except Exception as e:
        st.error(f"Log in has failed:{e}")

def signup_user(supabase_client, email:str, password: str):
    try:
        
        auth_response = supabase_client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": { 
                    "role": "user",
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

    