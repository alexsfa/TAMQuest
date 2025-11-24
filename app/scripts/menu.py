import streamlit as st
import streamlit as st
from scripts.authentication_functions import logout_user

MENU_CONFIG = {
    "user": [
        {"label": "Main page", "page": "app.py"},
        {"label": "Profile", "page": "pages/profile_page.py"},
    ],
    "admin": [
        {"label": "Main page", "page": "app.py"},
        {"label": "Profile", "page": "pages/profile_page.py"},
        {"label": "Admin activities", "page": "pages/admin_page.py"},
    ]
}

# The authenticated_menu() function renders the sidebar menu based on the user's role
def authenticated_menu(supabase_client):
    role = st.session_state.role
    for item in MENU_CONFIG.get(role, []):
        st.sidebar.page_link(item["page"], label=item["label"])
    st.sidebar.button("Logout", on_click= lambda: logout_user(supabase_client))

# The menu() function checks if user is authenticated.
# The unauthenticated users get redirect to the login page.
# For the authenticated users, the function calls the authenticated_menu function.
def menu(supabase_client):
    if "role" not in st.session_state:
        st.switch_page("pages/login_page.py")
        return
    authenticated_menu(supabase_client)