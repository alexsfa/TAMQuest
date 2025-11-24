import streamlit as st
from dotenv import load_dotenv
from scripts import supabase_client 
from scripts.menu import menu

# The environment vars are getting loaded for the whole process of the app
load_dotenv()

client = supabase_client.get_client()

# -----------------------------------------
# Below starts the UI of the app
# -----------------------------------------

if __name__ == "__main__":
    client = supabase_client.get_client()
    menu(client)

    st.title("Welcome to TAMQuest")
    st.write(st.session_state)