import streamlit as st

# sections of the sidebar menu based the user's role
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


'''
The sign_out function calls logout_user and deletes all the keys
that store the the user's session info and the ui state
'''


def sign_out(supabase_client):
    try:
        supabase_client.auth.sign_out()
    except Exception as e:
        st.error(f"Logout failed: {e}")

    delete_state = [
        "user_id",
        "profile_id",
        "role",
        "last_page",
        "current_response_id",
        "current_questionnaire_id",
        "edit_response_mode",
        "create_questionnaire",
        "add_questions",
        "show_preview",
        "create_profile",
        "update_profile",
        "delete_profile",
        "edit_response_mode"
    ]

    for key in delete_state:
        if key in st.session_state:
            del st.session_state[key]

    st.switch_page("pages/login_page.py")


'''
The authenticated_menu() function renders the
sidebar menu based on the user's role
'''


def authenticated_menu(supabase_client, role: str):
    role = st.session_state.role
    for item in MENU_CONFIG.get(role, []):
        st.sidebar.page_link(item["page"], label=item["label"])
    st.sidebar.button("Sign out", on_click=sign_out, args=(supabase_client,))


'''
The menu() function checks if user is authenticated.
The unauthenticated users get redirect to the login page.
For the authenticated users, the function calls the
authenticated_menu function.
'''


def menu(supabase_client):
    session = supabase_client.auth.get_session()

    if session is None or session.user is None:
        st.switch_page("pages/login_page.py")
        return

    user_data = session.user
    role = user_data.user_metadata.get("role", None)

    authenticated_menu(supabase_client, role)
