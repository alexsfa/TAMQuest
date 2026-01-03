import streamlit as st

from database.questions import Questions
from database.likert_scales import Likert_scales
from database.likert_scale_options import Likert_scale_options
from database.questions import Questions
from database.responses import Responses

from utils import supabase_client 
from utils.menu import menu

client = supabase_client.get_client()

responses_repo = Responses(client)
questions_repo = Questions(client)
likert_scales_repo = Likert_scales(client)
likert_scale_options_repo = Likert_scale_options(client)

if __name__ == "__main__":
    
    menu(client)

    st.write(st.session_state["current_questionnaire_id"])

    likert_scale_info = likert_scales_repo.get_likert_scale_by_questionnaire_id(st.session_state["current_questionnaire_id"])
    st.write(likert_scale_info)

    likert_scale_options = likert_scale_options_repo.get_options_by_likert_scale_id(likert_scale_info.data[0]["id"])
    st.write(likert_scale_options)

    questions_info = questions_repo.get_questions_by_questionnaire_id(st.session_state["current_questionnaire_id"])
    st.write(questions_info)

    responses_info = responses_repo.get_all_responses_by_questionnaire_id(st.session_state["current_questionnaire_id"])
    st.write(responses_info)

    unique_categories = list({item["category"] for item in questions_info.data})
    st.write(unique_categories)

    for category in unique_categories:
        st.write()


