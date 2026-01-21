import streamlit as st
import re
from datetime import datetime

from app import client, answers_repo, responses_repo

from database.answers import Answers
from database.responses import Responses

from services.response_services import retrieve_response_info

from utils import supabase_client 
from utils.menu import menu
from utils.logger_config import logger
from utils.components import format_time, set_answer_layout
        
if __name__ == "__main__":
    
    menu(client)
    response_info = retrieve_response_info(st.session_state["current_response_id"], responses_repo, answers_repo, logger)
    
    if response_info[0] is None:
        st.error("Error during the response's info retrieval! Try again later")
    else:
        st.title(response_info[0].data[0]["questionnaires"]['title'])
        st.write(f"Questionnaire description: {response_info[0].data[0]['questionnaires']['details']}")

        formatted_time = format_time(response_info[0].data[0]['submitted_at'])

        st.write(f"Submitted at {formatted_time}")
        st.write(f"By {response_info[0].data[0]['profiles']['full_name']}")
        
        for answer in response_info[1].data:
            set_answer_layout(answer)


    