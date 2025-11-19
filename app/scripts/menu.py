import streamlit as st
from datetime import date

def authenticated_menu():
    st.sidebar.page_link("app.py", label="Switch accounts")
    st.sidebar.page_link("pages/user.py", label="Profile")
    if st.session_state.role in ["admin"]:
        st.sidebar.page_link("pages/admin.py", label="Manage users")

def unauthenticated_menu():
    st.sidebar.page_link("app.py", label="Gain access")

# The menu function check if the session's user is authenticated,
# so it can show the appropriate for the occasion navigation menu.
def menu():
    if "role" not in st.session_state or st.session_state.role is None:
        unauthenticated_menu()
        return
    authenticated_menu()

# The menu_with_redirect function redirects the unaunthenticated users to the main page
def menu_with_redirect():
    if "role" not in st.session_state or st.session_state.role is None:
        st.switch_page("app")
    menu()