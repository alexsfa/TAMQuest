import streamlit as st

from app import client, answers_repo, responses_repo

from services.response_services import retrieve_response_info

from utils.menu import menu
from utils.logger_config import logger
from utils.components import format_time, set_answer_layout
from utils.redirections import redirect_to_login_page

if __name__ == "__main__":

    redirect_to_login_page()

    menu(client)
    response_info = retrieve_response_info(
        st.session_state["current_response_id"],
        responses_repo,
        answers_repo,
        logger
    )

    if response_info[0] is None:
        st.error("Error during the response's info retrieval! Try again later")
    else:
        st.title(response_info[0].data[0]["questionnaires"]['title'])
        st.write(
            "Questionnaire description:"
            f"{response_info[0].data[0]['questionnaires']['details']}"
        )

        formatted_time = format_time(response_info[0].data[0]['submitted_at'])

        st.write(f"Submitted at {formatted_time}")
        st.write(f"By {response_info[0].data[0]['profiles']['full_name']}")

        for answer in response_info[1].data:
            set_answer_layout(answer)
