import streamlit as st
import html, re
from datetime import datetime
from scripts import supabase_client 
from scripts.menu import menu

current_page = "profile_page"

if __name__ == "__main__":
    client = supabase_client.get_client()
    menu(client)
    st.session_state.last_page = current_page

    st.title("Welcome to your profile")

    st.title("Your responses")

    responses = client.table("responses").select("questionnaires(*), submitted_at, is_submitted").eq("user_id", st.session_state["user_id"]).order("is_submitted", desc=True).execute()

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
                        <small>Subitted at: {formatted_time}</small><br>
                    </article>
                    """, unsafe_allow_html=True)
                
            with col2:
                respond_key = f"edit_{item['questionnaires']['id']}"
                if st.button("View", key=respond_key):
                    redirect_to_respond_page(item['id'])

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
                        redirect_to_respond_page(item['id'])
    