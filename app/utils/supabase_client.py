import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

'''
The init_client() retrieves the supabase_url and anon_key from environment vars,
so it can initialize and store in session_state a new supabase client
'''
def init_client() -> Client:
    supabase_url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("ANON_KEY")

    client: Client = create_client(supabase_url, anon_key)
    st.session_state["supabase"] = client
    return client

'''
The get_client() function checks if there is a supabase client stored in the app's session state,
if there isn't, the init_client() function is called
'''
def get_client() -> Client:
    if "supabase" not in st.session_state:
        init_client()
    return st.session_state["supabase"]

