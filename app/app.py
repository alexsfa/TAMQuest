import streamlit as st
from dotenv import load_dotenv
from scripts.menu import menu



# The environment vars are getting loaded for the whole process of the app
load_dotenv()

if "role" not in st.session_state:
    st.switch_page("pages/login_page.py")

# -----------------------------------------
# Below starts the UI of the app
# -----------------------------------------

st.title("Welcome to TAMQuest")

menu()
