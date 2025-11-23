import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

# The supabase_client_init() retrieves the supabase_url and anon_key from environment vars,
# so it can initialize and store in session_state a new supabase_client
def supabase_client_init() -> Client:
    supabase_url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("ANON_KEY")
    st.session_state["supabase"] = create_client(supabase_url, anon_key)

# The get_supabase_function() checks if there is a supabase client stored in the app's session state,
# if there isn't, the supabase_client_init() function is called
def check_supabase_client() -> Client:
    if "supabase" not in st.session_state:
        supabase_client_init()
    return st.session_state["supabase"]

