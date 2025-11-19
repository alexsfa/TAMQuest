import os
from scripts.menu import menu
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
    st.switch_page("pages/login_page.py")





# -----------------------------------------
# Below starts the UI of the app
# -----------------------------------------

st.title("Private App Login")
