from datetime import date
import streamlit as st
from scripts import authentication_functions as auth

load_dotenv()

SUPABASE_KEY = os.getenv("ANON_KEY")

BASE_URL = os.getenv("SUPABASE_URL")
supabase: Client = create_client(BASE_URL, SUPABASE_KEY)

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
        if st.button("Sign up"):
            auth.signup_user(email, password, name, birthdate)

elif auth_action == "Login":
    if st.button("Login"):
        auth.login_user(email, password)
