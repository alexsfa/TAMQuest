import streamlit as st
import re
import html
from datetime import datetime
from dotenv import load_dotenv
from scripts import supabase_client 
from scripts.menu import menu

# The environment vars are getting loaded for the whole process of the app
load_dotenv()

client = supabase_client.get_client()

current_page = "main_page"

# -----------------------------------------
# Below starts the UI of the app
# -----------------------------------------
def delete_questionnaire(questionnaire_id: str):
    response = client.table("questionnaires").delete().eq("id", questionnaire_id).execute()

    if len(response.data) == 0:
        return f"Error deleting questionnaire"
    else:
        st.rerun()

def redirect_to_respond_page(questionnaire_id: str):
    st.session_state["current_response_id"] = questionnaire_id
    st.switch_page("pages/questionnaire_response_page.py")

if __name__ == "__main__":
    client = supabase_client.get_client()
    menu(client)
    st.session_state.last_page = current_page

    st.title("Welcome to TAMQuest")

    st.write("## Available questionnaires")

    qs = client.table("questionnaires").select("*").execute()

    if len(qs.data) == 0:
        st.write("There are no questionnaires available for response")
    else:
        questionnaire_list = qs.data

        for item in questionnaire_list:
            title_safe = html.escape(item['title'])

            if item['details'] is None:
                details_safe = "No details were provided."
            else: 
                details_safe = html.escape(item['details'])

            raw = item["created_at"]
            raw = re.sub(
                r"\.(\d{5})(\+|\-)",   # match .12345+00
                lambda m: f".{m.group(1)}0{m.group(2)}", 
                raw
            )
            dt = datetime.fromisoformat(raw)
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S %Z")

            questionnaire_card = st.container()

            col1, col2, col3 = st.columns([5,1,1])
        
            with col1:
                st.markdown(f"""
                    <article style='
                        border: 4px solid #000000; 
                        background-color: #E4EDA6;
                        padding:8px;
                        border-radius:8px;
                        margin-bottom:12px;
                        text-align: center;'>
                        <h3>{title_safe}</h3>
                        <p style='font-size:18px;'>{details_safe}</p>
                        <small>Created at: {formatted_time}</small><br>
                    </article>
                    """, unsafe_allow_html=True)
                
            with col2:
                respond_key = f"respond_{item['id']}"
                if st.button("Respond", key=respond_key):
                    redirect_to_respond_page(item['id'])

            message_box = st.empty()

            if st.session_state.role == 'admin':
                with col3:
                    delete_key = f"delete_{item['id']}"
                    if st.button("Delete", key=delete_key):
                        msg = delete_questionnaire(item['id'])
                        message_box.error(msg)
        
                st.write("\n")