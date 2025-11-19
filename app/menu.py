import streamlit as st

def authenticated_menu():
    st.sidebar.page_link("app.py", label="Switch accounts")
    st.sidebar.page_link("pages/user.py", label="Your TAMQuest Profile")
    if st.session_state.role in ["admin"]:
        st.sidebar.page_link("pages/admin.py", label="Manage users")

def unauthenticated_menu():
    st.sidebar.page_link("app.py", label="Gain access")

def menu():
    if "role" not in st.session_state or st.session_state.role is None:
        unauthenticated_menu()
        return
    authenticated_menu()

def menu_with_redirect():
    if "role" not in st.session_state or st.session_state.role is None:
        st.switch_page("app")
    menu()