import streamlit as st
from datetime import date
import html, re
from datetime import datetime
from scripts import supabase_client 
from scripts.menu import menu

current_page = "profile_page"


def redirect_to_view_page(questionnaire_id: str):
    st.session_state["current_response_id"] = questionnaire_id
    st.switch_page("pages/response_view_page.py")

if __name__ == "__main__":
    st.write(st.session_state)
    client = supabase_client.get_client()
    menu(client)
    st.session_state.last_page = current_page

    st.title("Welcome to your profile")

    user_profile = client.table("profiles").select("*").eq("id", st.session_state["user_id"]).execute()

    if not user_profile.data:
        if "create_profile" not in st.session_state:
            st.session_state.create_profile = False



        if st.button("Create your profile"):
            st.session_state.create_profile = not st.session_state.create_profile
        
        if st.session_state.create_profile:
            username = st.text_input("Your name", key="username")
            birthdate = st.date_input(
                        "Birthdate", 
                        max_value=date.today(),
                        min_value=date(1900, 1, 1))
            city = st.text_input("Your city", key="user_city")
            country = st.text_input("Your country", key="user_country")

            if st.button("Save changes"):
                st.write(birthdate.isoformat())
                profile_insert = client.table("profiles").insert({
                    "id": st.session_state["user_id"],
                    "full_name": username,
                    "birthdate": birthdate.isoformat(),
                    "city": city,
                    "country": country
                }).execute()
                st.write(profile_insert)

    st.title("Your responses")

    responses = client.table("responses").select("questionnaires(*), id, submitted_at, is_submitted").eq("user_id", st.session_state["user_id"]).order("is_submitted", desc=True).execute()

    drafts = [r for r in responses.data if not r["is_submitted"]]
    submitted = [r for r in responses.data if r["is_submitted"]]

    if len(submitted) == 0:
        st.write("There are no responses")
    else:

        for item in submitted:

            title_safe = html.escape(item['questionnaires']['title'])

            raw = item["submitted_at"]
            raw = re.sub(
                r"\.(\d{5})(\+|\-)",   # match .12345+00
                lambda m: f".{m.group(1)}0{m.group(2)}", 
                raw
            )
            dt = datetime.fromisoformat(raw)
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S %Z")

            col1, col2 = st.columns([3,1])
        
            with col1:
                st.markdown(f"""
                    <article style='
                        border: 4px solid #000000; 
                        background-color: #E4EDA6;
                        padding:8px;
                        border-radius:8px;
                        margin-bottom:12px;
                        text-align: center;'>
                        <small>Response for:</small><br>
                        <h3>{title_safe}</h3>
                        <small>Submitted at: {formatted_time}</small><br>
                    </article>
                    """, unsafe_allow_html=True)
                
            with col2:
                respond_key = f"view_{item['id']}"
                if st.button("View", key=respond_key):
                    redirect_to_view_page(item['id'])

    st.title("Your drafts")

    if len(drafts) == 0:
        st.write("There are no drafts")
    else:

        for item in drafts:

            title_safe = html.escape(item['questionnaires']['title'])

            raw = item["submitted_at"]
            raw = re.sub(
                r"\.(\d{5})(\+|\-)",   # match .12345+00
                lambda m: f".{m.group(1)}0{m.group(2)}", 
                raw
            )
            dt = datetime.fromisoformat(raw)
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S %Z")

            col1, col2 = st.columns([3,1])
        
            with col1:
                st.markdown(f"""
                    <article style='
                        border: 4px solid #000000; 
                        background-color: #E4EDA6;
                        padding:8px;
                        border-radius:8px;
                        margin-bottom:12px;
                        text-align: center;'>
                        <small>Response draft for:</small><br>
                        <h3>{title_safe}</h3>
                        <small>Saved at: {formatted_time}</small><br>
                    </article>
                    """, unsafe_allow_html=True)
                
            with col2:
                respond_key = f"edit_{item['questionnaires']['id']}"
                if st.button("Edit", key=respond_key):
                    redirect_to_view_page(item['id'])
    