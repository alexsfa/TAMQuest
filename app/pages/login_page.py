import os
import streamlit as st
from datetime import date
from dotenv import load_dotenv
from scripts import authentication_functions as auth
from scripts import supabase_client 
from supabase import create_client, Client

if __name__ == "__main__":
    client = supabase_client.get_client()

    st.header("This app is private.")
    st.subheader("Please log in.")

    auth_action = st.selectbox("Choose action", ["Login", "Sign up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if auth_action == "Sign up":
        name = st.text_input("Name")
        birthdate = st.date_input(
                        "Birthdate", 
                        max_value=date.today(),
                        min_value=date(1900, 1, 1))
        if st.button("Sign Up"):
            auth.signup_user(client, email, password, name, birthdate)

    elif auth_action == "Login":
        if st.button("Login"):
            logged_user = auth.login_user(client, email, password)

            if logged_user:
                st.session_state["role"] = logged_user.user.app_metadata.get("role", "user")
                st.session_state["user_id"] = logged_user.user.id
                
                st.switch_page("app.py")
