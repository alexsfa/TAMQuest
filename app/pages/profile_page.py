import streamlit as st
from scripts import supabase_client 
from scripts.menu import menu

current_page = "profile_page"

if __name__ == "__main__":
    client = supabase_client.get_client()
    menu(client)
    st.session_state.last_page = current_page

    st.title("Welcome to your profile")

    st.write("Available questionnaires")