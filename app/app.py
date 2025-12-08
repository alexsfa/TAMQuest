import streamlit as st
import re
import html
from datetime import datetime
from dotenv import load_dotenv

from database.questionnaires import Questionnaires

from utils import supabase_client 
from utils.menu import menu
from utils.redirections import redirect_to_respond_page, redirect_to_view_page
from utils.logger_config import logger

# The environment vars are getting loaded for the whole process of the app
load_dotenv()

client = supabase_client.get_client()
questionnaires_repo = Questionnaires(client)

current_page = "main_page"

# -----------------------------------------
# Below starts the UI of the app
# -----------------------------------------


def delete_response(response_id: str):
    response = client.table("responses").delete().eq("id", response_id).execute()

    if len(response.data) == 0:
        return f"Error deleting response"
    else:
        st.rerun()

if __name__ == "__main__":
    menu(client)
    st.session_state.last_page = current_page

    st.title("Welcome to TAMQuest")

    
    if st.session_state["role"] == 'admin':
        st.write("## User's responses")
        responses = client.table("responses").select("questionnaires(*), profiles(full_name), id, submitted_at, is_submitted").eq("is_submitted", True).order("submitted_at", desc=True).execute()

        if len(responses.data) == 0:
            st.write("There are not any responses for the questionnaires")
        else:
            response_list = responses.data

            for item in response_list:
                title_safe = html.escape(item['questionnaires']['title'])

                raw = item["submitted_at"]
                raw = re.sub(
                    r"\.(\d+)(?=[+-])",
                    lambda m: "." + (m.group(1) + "000000")[:6],
                    raw
                )
                dt = datetime.fromisoformat(raw)
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S %Z")

                response_card = st.container()

                col1, col2, col3 = st.columns([5,0.7,1])

                response_owner = html.escape(item['profiles']['full_name'])
        
                with col1:
                    st.markdown(f"""
                        <article style='
                            border: 4px solid #000000; 
                            background-color: #E4EDA6;
                            padding:8px;
                            border-radius:8px;
                            margin-bottom:12px;
                            text-align: center;'>
                            <p style='font-size:18px; margin-top:4px; margin-bottom:0px;'>Response for</p>
                            <h3 style=' margin-bottom:0px;'>{title_safe}</h3>
                            <small>Submitted at: {formatted_time}</small><br>
                            <small>By: {response_owner}</small><br>
                        </article>
                        """, unsafe_allow_html=True)
                
                with col2:
                    respond_key = f"view_{item['id']}"
                    if st.button("View", key=respond_key):
                        redirect_to_view_page(item['id'])

                message_box = st.empty()

                with col3:
                    delete_key = f"delete_{item['id']}"
                    if st.button("Delete", key=delete_key):
                        msg = delete_response(item['id'])
                        message_box.error(msg)

    else:
        
        qs = None
        try:
            qs = questionnaires_repo.questionnaires_without_user_response(st.session_state["user_id"])
        except RuntimeError as e:
            logger.error(f"Database error: {e}")
        
        if qs is None:
            st.error(f"Error during the questionnaires retrieval: {e}")
        elif len(qs.data) == 0:
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
                    r"\.(\d+)(?=[+-])",
                    lambda m: "." + (m.group(1) + "000000")[:6],
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